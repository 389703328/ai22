/**
 * Common types used across the application
 */
export interface ApiResponse<T = any> {
  data: T;
  message?: string;
  status: number;
}

export interface PaginatedResponse<T> {
  items: T[];
  total: number;
  page: number;
  limit: number;
  offset: number;
}

export interface ApiError {
  detail: string;
  status?: number;
}

export interface SelectOption {
  label: string;
  value: string | number;
}

export interface TableColumn {
  prop: string;
  label: string;
  width?: string | number;
  sortable?: boolean;
}