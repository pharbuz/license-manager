import {
  useMutation,
  useQuery,
  useQueryClient,
  type UseMutationOptions,
} from "@tanstack/react-query";
import type { ApiError } from "../api";
import {
  createCustomer,
  deleteCustomer,
  getCustomer,
  listCustomers,
  updateCustomer,
} from "../services";
import type {
  CollectionPage,
  Customer,
  CustomerCreateInput,
  CustomerUpdateInput,
  ListQueryParams,
  Uuid,
} from "../types";
import { buildCollectionPage } from "../utils/client-pagination";
import { queryKeys } from "./query-keys";
import { getCollectionUiState } from "./use-query-states";

export function useCustomers(params?: ListQueryParams) {
  const query = useQuery<Customer[], ApiError>({
    queryKey: queryKeys.customers.list(),
    queryFn: () => listCustomers(),
  });

  const pagination: CollectionPage<Customer> | undefined = query.data
    ? buildCollectionPage({
        items: query.data,
        page: params?.page,
        size: params?.size,
        search: params?.search,
        searchValues: (customer) => [
          customer.customerSymbol,
          customer.name,
          customer.email,
          customer.contactPersonName,
          customer.contactPersonPhone,
        ],
      })
    : undefined;

  const collectionState = getCollectionUiState(pagination, query.isSuccess);

  return {
    ...query,
    items: pagination?.items ?? [],
    pagination,
    ...collectionState,
  };
}

export function useCustomer(customerId?: Uuid) {
  return useQuery<Customer, ApiError>({
    queryKey: queryKeys.customers.detail(customerId ?? ""),
    queryFn: () => getCustomer(customerId as Uuid),
    enabled: Boolean(customerId),
  });
}

export function useCreateCustomer(
  options?: UseMutationOptions<Customer, ApiError, CustomerCreateInput>,
) {
  const queryClient = useQueryClient();
  const { onSuccess, ...mutationOptions } = options ?? {};

  return useMutation<Customer, ApiError, CustomerCreateInput>({
    ...mutationOptions,
    mutationFn: (payload) => createCustomer(payload),
    onSuccess: async (data, variables, onMutateResult, context) => {
      await queryClient.invalidateQueries({
        queryKey: queryKeys.customers.all,
      });
      await onSuccess?.(data, variables, onMutateResult, context);
    },
  });
}

export function useUpdateCustomer(
  options?: UseMutationOptions<
    Customer,
    ApiError,
    { customerId: Uuid; payload: CustomerUpdateInput }
  >,
) {
  const queryClient = useQueryClient();
  const { onSuccess, ...mutationOptions } = options ?? {};

  return useMutation<
    Customer,
    ApiError,
    { customerId: Uuid; payload: CustomerUpdateInput }
  >({
    ...mutationOptions,
    mutationFn: ({ customerId, payload }) =>
      updateCustomer(customerId, payload),
    onSuccess: async (data, variables, onMutateResult, context) => {
      await Promise.all([
        queryClient.invalidateQueries({ queryKey: queryKeys.customers.all }),
        queryClient.invalidateQueries({
          queryKey: queryKeys.customers.detail(variables.customerId),
        }),
      ]);
      await onSuccess?.(data, variables, onMutateResult, context);
    },
  });
}

export function useDeleteCustomer(
  options?: UseMutationOptions<void, ApiError, Uuid>,
) {
  const queryClient = useQueryClient();
  const { onSuccess, ...mutationOptions } = options ?? {};

  return useMutation<void, ApiError, Uuid>({
    ...mutationOptions,
    mutationFn: (customerId) => deleteCustomer(customerId),
    onSuccess: async (data, customerId, onMutateResult, context) => {
      await Promise.all([
        queryClient.invalidateQueries({ queryKey: queryKeys.customers.all }),
        queryClient.removeQueries({
          queryKey: queryKeys.customers.detail(customerId),
        }),
      ]);
      await onSuccess?.(data, customerId, onMutateResult, context);
    },
  });
}
