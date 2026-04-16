import { apiRequest } from "../api";
import type {
  Customer,
  CustomerCreateInput,
  CustomerUpdateInput,
  Uuid,
} from "../types";

export function listCustomers() {
  return apiRequest<Customer[]>({
    method: "GET",
    url: "/customers",
  });
}

export function getCustomer(customerId: Uuid) {
  return apiRequest<Customer>({
    method: "GET",
    url: `/customers/${customerId}`,
  });
}

export function createCustomer(payload: CustomerCreateInput) {
  return apiRequest<Customer>({
    method: "POST",
    url: "/customers",
    data: payload,
  });
}

export function updateCustomer(customerId: Uuid, payload: CustomerUpdateInput) {
  return apiRequest<Customer>({
    method: "PATCH",
    url: `/customers/${customerId}`,
    data: payload,
  });
}

export function deleteCustomer(customerId: Uuid) {
  return apiRequest<void>({
    method: "DELETE",
    url: `/customers/${customerId}`,
  });
}
