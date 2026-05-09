# Руководство: Подключение умных счетчиков Tuya к сторонней B2B-платформе

## Шаг 1. Регистрация и создание Cloud Project

Вам необходимо создать среду, в которой будут жить API-ключи и куда будут привязываться счетчики.

1.  Зарегистрируйте корпоративный аккаунт на [Tuya IoT Platform](https://iot.tuya.com/).
2.  Перейдите в раздел **Cloud** -\> **Development** и нажмите **Create Cloud Project**.
3.  При создании выберите индустрию (например, *Smart Home* или *Industry Solutions*) и нужный дата-центр (для Европы/РФ обычно выбирают *Central Europe Data Center* или *Western Europe*).
4.  После создания проекта вы получите **Access ID (Client ID)** и **Access Secret (Client Secret)**. Это ваши главные ключи для API.
5.  В настройках проекта перейдите на вкладку **Service API** и убедитесь, что у вас активированы базовые пакеты: *IoT Core*, *Authorization Token Management* и *Data Dashboard Service*.

🔗 **Официальная документация:** [Cloud Development Quick Start](https://developer.tuya.com/en/docs/iot/quick-start1?id=K95ztz9u9t89n)

-----

## Шаг 2. Авторизация и привязка счетчиков (Device Linking)

Облако Tuya должно знать, какими устройствами вы имеете право управлять. Для B2B-проектов (ЖК) есть два основных пути импорта устройств в ваш Cloud Project:

  * **Метод Asset Management (Рекомендуемый для ЖК):** Внутри проекта вы создаете "Активы" (Assets) — например, "Дом 1", "Дом 2". Монтажники при установке счетчиков через специальное инженерное приложение или по серийным номерам привязывают устройства к этим Активам.
  * **Метод App Account Linking (Для тестов):** Вы скачиваете приложение Tuya Smart, добавляете туда счетчики по Wi-Fi/Zigbee, а затем в Cloud Project во вкладке **Devices -\> Link Tuya App Account** сканируете QR-код. Все устройства из приложения появятся в API.

🔗 **Официальная документация:** \* [Asset & Device Management](https://www.google.com/search?q=https://developer.tuya.com/en/docs/iot/asset-management%3Fid%3DK9i5ql5weozw3)

  * [Link Devices to Cloud Project](https://www.google.com/search?q=https://developer.tuya.com/en/docs/iot/device-management%3Fid%3DK9g6rfntdqz2s)

-----

## Шаг 3. Интеграция SDK (Чтобы не писать шифрование с нуля)

Tuya использует сложную систему подписи каждого API-запроса (HMAC-SHA256 с учетом таймстемпов, nonce и тела запроса). Чтобы не тратить недели на отладку хэшей, **обязательно** используйте официальные SDK для вашего бэкенда.

Они доступны для Node.js, Python, Java, Go и C\#. SDK берет на себя обновление токенов доступа и подпись запросов.

🔗 **Официальная документация:** [Tuya Cloud SDK Download & Setup](https://www.google.com/search?q=https://developer.tuya.com/en/docs/iot/developer-guide%3Fid%3DKamchp3v17vki)

-----

## Шаг 4. Настройка входящего потока данных (Pulsar Message Queue)

Как уже упоминалось, для B2B *строго запрещено* использовать постоянные GET-запросы (Polling) для сбора показаний. Вам нужно настроить подписку на события.

1.  В вашем Cloud Project перейдите на вкладку **Message Queue**.
2.  Включите ее. Платформа выдаст вам параметры для подключения.
3.  В официальном Tuya SDK уже встроен клиент для очереди. Вы запускаете его как фоновый сервис (демон) на вашем сервере.
4.  Как только любой счетчик в ЖК меняет показания (изменилась мощность, прошел киловатт-час, сработало реле), облако Tuya отправляет JSON-сообщение в этот канал.
5.  Ваш сервис принимает сообщение в реальном времени (latency \~1-2 секунды) и записывает в вашу БД (PostgreSQL, InfluxDB и т.д.).

**Пример структуры входящего push-сообщения (Pulsar):**

```json
{
  "dataId": "111222333",
  "devId": "vbf1234567890abcdef", 
  "productKey": "...",
  "status": [
    { "code": "forward_energy_total", "value": 145620, "t": 1698765432100 }
  ]
}
```

🔗 **Официальная документация:** [Message Queue (Data Push Service)](https://www.google.com/search?q=https://developer.tuya.com/en/docs/iot/message-queue%3Fid%3DK9m9x9oigk1n3)

-----

## Шаг 5. Отправка команд и синхронизация (REST API)

Даже при использовании Message Queue вам понадобится REST API для отправки команд (например, отключить должника) и первичного сбора данных о счетчиках.

**1. Получение списка всех счетчиков в вашем ЖК (синхронизация базы):**
Вы можете запросить все устройства, привязанные к вашему проекту (или к конкретному Asset ID), чтобы заполнить свою базу данных Device ID.

  * `GET /v1.0/iot-02/assets/{asset_id}/devices`

**2. Отправка команды на счетчик:**
Если оператор в вашем ПО нажимает кнопку "Отключить электричество в Квартире 15".

  * `POST /v1.0/iot-03/devices/{device_id}/commands`
  * *(Подробности параметров `switch`, `clear_energy` и др. для счетчиков мы разбирали ранее)*.

🔗 **Официальная документация:** \* [Device Control API (Команды)](https://developer.tuya.com/en/docs/iot/device-control?id=K9vc440qrbqyf)

  * [Query Device Information (Информация)](https://www.google.com/search?q=https://developer.tuya.com/en/docs/iot/query-device-details%3Fid%3DK9vc440rb16t2)

-----

## Архитектурное резюме (Как работает ваш код)

Ваш B2B-бэкенд (на Node.js, Python или Java) будет состоять из двух независимых модулей:

1.  **Модуль слушателя (Listener Service):**
      * Постоянно держит открытое соединение с Tuya Pulsar Message Queue.
      * Принимает сырые данные по метрикам (`forward_energy_total`, `phase_a`, `fault`).
      * Применяет коэффициенты (Scale: делит на 10, 100, 1000).
      * Сохраняет чистые кВт·ч, Вольты и Амперы в базу данных (например, в TimescaleDB для графиков).
2.  **Модуль управления (API Server):**
      * Принимает команды от фронтенда вашего интерфейса (кабинета УК).
      * Через Tuya SDK отправляет `POST` запросы в облако Tuya на конкретный `device_id`, чтобы включить/выключить реле или сменить настройки защиты счетчика.

Такой подход обеспечит стабильную работу без блокировок по Rate Limits даже на 10 000+ счетчиков.