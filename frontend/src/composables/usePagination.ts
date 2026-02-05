/**
 * Pagination composable for reusable pagination logic
 */
import { ref, computed } from 'vue';

export function usePagination(initialPage = 1, initialLimit = 20) {
  const page = ref(initialPage);
  const limit = ref(initialLimit);
  const total = ref(0);

  const offset = computed(() => (page.value - 1) * limit.value);
  const totalPages = computed(() => Math.ceil(total.value / limit.value));

  const nextPage = () => {
    if (page.value < totalPages.value) {
      page.value += 1;
    }
  };

  const prevPage = () => {
    if (page.value > 1) {
      page.value -= 1;
    }
  };

  const goToPage = (pageNum: number) => {
    if (pageNum >= 1 && pageNum <= totalPages.value) {
      page.value = pageNum;
    }
  };

  const setTotal = (newTotal: number) => {
    total.value = newTotal;
  };

  const reset = () => {
    page.value = initialPage;
    limit.value = initialLimit;
    total.value = 0;
  };

  return {
    page,
    limit,
    total,
    offset,
    totalPages,
    nextPage,
    prevPage,
    goToPage,
    setTotal,
    reset
  };
}