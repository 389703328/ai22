<template>
  <el-button
    :type="type"
    :size="size"
    :loading="loading"
    :disabled="disabled"
    :icon="icon"
    :plain="plain"
    :round="round"
    :circle="circle"
    @click="handleClick"
  >
    <slot />
  </el-button>
</template>

<script setup lang="ts">
import { ElButton } from 'element-plus';

interface Props {
  type?: 'primary' | 'success' | 'warning' | 'danger' | 'info' | 'text' | 'default';
  size?: 'large' | 'default' | 'small';
  loading?: boolean;
  disabled?: boolean;
  icon?: string;
  plain?: boolean;
  round?: boolean;
  circle?: boolean;
}

interface Emits {
  click: [event: MouseEvent];
}

const props = withDefaults(defineProps<Props>(), {
  type: 'default',
  size: 'default',
  loading: false,
  disabled: false,
  plain: false,
  round: false,
  circle: false
});

const emit = defineEmits<Emits>();

const handleClick = (event: MouseEvent) => {
  emit('click', event);
};
</script>

<style scoped>
/* Custom button styles can be added here */
</style>