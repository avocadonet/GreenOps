import asyncio
import logging
import asyncpg
from datetime import datetime, timedelta
from typing import Optional, Dict, List, Tuple
import os

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://user:password@postgres:5432/greenops_db")
REDIS_URL = os.getenv("REDIS_URL", "redis://redis:6379")

logger = logging.getLogger("ThresholdManager")

class ThresholdManager:
    def __init__(self):
        self.pg_pool = None
        self.redis = None
        self.update_interval_hours = 6
        self.anomaly_percentage = 30
        
    async def initialize(self):
        try:
            self.pg_pool = await asyncpg.create_pool(DATABASE_URL)
            logger.info("ThresholdManager: Connected to PostgreSQL")
            
            from redis import asyncio as aioredis
            self.redis = await aioredis.from_url(REDIS_URL, decode_responses=True)
            logger.info("ThresholdManager: Connected to Redis")
            
            return True
        except Exception as e:
            logger.error(f"ThresholdManager initialization failed: {e}")
            return False
    
    async def calculate_building_average(self, building_id: int, hours_back: int = 24) -> Optional[float]:
        
        try:
            async with self.pg_pool.acquire() as conn:
                result = await conn.fetchval("""
                    SELECT AVG(value) as avg_value
                    FROM energy_metrics
                    WHERE building_id = $1
                        AND timestamp >= NOW() - INTERVAL '1 hour' * $2
                        AND value IS NOT NULL
                """, building_id, hours_back)
                
                if result is None:
                    logger.warning(f"No data for building {building_id} in last {hours_back} hours")
                    return None
                
                logger.info(f"Building {building_id} average consumption: {result:.2f} kWh")
                return float(result)
                
        except Exception as e:
            logger.error(f"Error calculating average for building {building_id}: {e}")
            return None
    
    async def calculate_all_buildings_averages(self) -> Dict[int, float]:
        
        averages = {}
        try:
            async with self.pg_pool.acquire() as conn:
                buildings = await conn.fetch("""
                    SELECT DISTINCT building_id 
                    FROM energy_metrics
                    WHERE building_id IS NOT NULL
                """)
                
                for record in buildings:
                    building_id = record['building_id']
                    avg_value = await self.calculate_building_average(building_id)
                    if avg_value is not None:
                        averages[building_id] = avg_value
                        
        except Exception as e:
            logger.error(f"Error calculating all buildings averages: {e}")
            
        return averages
    
    def calculate_dynamic_threshold(self, average_value: float) -> float:
        
        if average_value is None:
            return None
            
        threshold = average_value * (1 + self.anomaly_percentage / 100)
        return threshold
    
    async def update_thresholds(self):
        
        logger.info("Starting threshold update cycle...")
        
        try:
            averages = await self.calculate_all_buildings_averages()
            
            if not averages:
                logger.warning("No averages calculated, skipping threshold update")
                return
            
            updated_count = 0
            for building_id, avg_value in averages.items():
                dynamic_threshold = self.calculate_dynamic_threshold(avg_value)
                
                if dynamic_threshold is not None:
                    await self.redis.set(
                        f"building:{building_id}:threshold",
                        dynamic_threshold
                    )
                    
                    await self.redis.set(
                        f"building:{building_id}:average_consumption",
                        avg_value
                    )
                    
                    await self.redis.set(
                        f"building:{building_id}:threshold_updated_at",
                        datetime.now().isoformat()
                    )
                    
                    updated_count += 1
                    logger.info(
                        f"Updated threshold for building {building_id}: "
                        f"avg={avg_value:.2f} kWh, threshold={dynamic_threshold:.2f} kWh "
                        f"(+{self.anomaly_percentage}%)"
                    )
            
            logger.info(f"Threshold update completed. Updated {updated_count} buildings")
            
        except Exception as e:
            logger.error(f"Error in update_thresholds: {e}")
    
    async def run_periodic_updates(self):
        
        logger.info(f"Starting periodic threshold updates every {self.update_interval_hours} hours")
        
        while True:
            try:
                await self.update_thresholds()
                
                await asyncio.sleep(self.update_interval_hours * 3600)
                
            except asyncio.CancelledError:
                logger.info("Periodic updates cancelled")
                break
            except Exception as e:
                logger.error(f"Error in periodic updates: {e}")
                await asyncio.sleep(3600)
    
    async def get_threshold_info(self, building_id: int) -> dict:
        
        try:
            threshold = await self.redis.get(f"building:{building_id}:threshold")
            avg = await self.redis.get(f"building:{building_id}:average_consumption")
            updated_at = await self.redis.get(f"building:{building_id}:threshold_updated_at")
            
            return {
                "building_id": building_id,
                "current_threshold": float(threshold) if threshold else None,
                "average_consumption": float(avg) if avg else None,
                "anomaly_percentage": self.anomaly_percentage,
                "last_updated": updated_at,
                "update_interval_hours": self.update_interval_hours
            }
        except Exception as e:
            logger.error(f"Error getting threshold info: {e}")
            return {}
    
    async def cleanup(self):
        
        if self.pg_pool:
            await self.pg_pool.close()
        if self.redis:
            await self.redis.close()