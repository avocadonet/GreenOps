import { computed } from 'vue';
import { useAuth } from './useAuth.js';

const ROLE_PRIORITY = {
  SUPER_USER: 0,
  SUPER_OWNER: 1,
  SUPER_ADMIN: 2,
  SUPER_REDACTOR: 3,
  ORGANIZATION_OWNER: 4,
  ADMIN: 5,
  REDACTOR: 6,
  OWNER: 7,
  PUBLIC: 8,
};

// minimum priority level required to access each view (lower = higher privilege)
const VIEW_MIN_PRIORITY = {
  dashboard: 7,        // any org member (OWNER+) — dashboard reads org/unit data
  organizations: 4,    // ORGANIZATION_OWNER and above only
  users: 7,
  buildings: 7,
  units: 7,
  sensors: 7,
  thresholds: 7,
};

export function usePermissions() {
  const { user, orgRoles } = useAuth();

  const effectivePriority = computed(() => {
    const globalPriority = ROLE_PRIORITY[user.value?.role] ?? 8;
    const orgBest = (orgRoles.value ?? []).reduce(
      (best, r) => Math.min(best, ROLE_PRIORITY[r.role] ?? 8),
      8
    );
    return Math.min(globalPriority, orgBest);
  });

  const canAccess = (view) => effectivePriority.value <= (VIEW_MIN_PRIORITY[view] ?? 8);

  const allowedViews = computed(() =>
    Object.keys(VIEW_MIN_PRIORITY).filter(v => canAccess(v))
  );

  return { effectivePriority, allowedViews, canAccess };
}
