import { apiRequest } from "../api";
import type {
  Product,
  ProductCreateInput,
  ProductUpdateInput,
  Uuid,
} from "../types";

export function listProducts() {
  return apiRequest<Product[]>({
    method: "GET",
    url: "/products",
  });
}

export function getProduct(productId: Uuid) {
  return apiRequest<Product>({
    method: "GET",
    url: `/products/${productId}`,
  });
}

export function createProduct(payload: ProductCreateInput) {
  return apiRequest<Product>({
    method: "POST",
    url: "/products",
    data: payload,
  });
}

export function updateProduct(productId: Uuid, payload: ProductUpdateInput) {
  return apiRequest<Product>({
    method: "PATCH",
    url: `/products/${productId}`,
    data: payload,
  });
}

export function deleteProduct(productId: Uuid) {
  return apiRequest<void>({
    method: "DELETE",
    url: `/products/${productId}`,
  });
}
