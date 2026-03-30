import { ref } from 'vue';

export function useLocalStore(storageKey, idField) {
  const load = () => JSON.parse(localStorage.getItem(storageKey) || '[]');
  const items = ref(load());

  const persist = () => localStorage.setItem(storageKey, JSON.stringify(items.value));

  const upsert = (item) => {
    const idx = items.value.findIndex(i => i[idField] === item[idField]);
    if (idx >= 0) items.value[idx] = item;
    else items.value.unshift(item);
    persist();
  };

  const remove = (id) => {
    items.value = items.value.filter(i => i[idField] !== id);
    persist();
  };

  return { items, upsert, remove };
}
