import { afterEach, describe, expect, it, vi } from "vitest";
import * as api from "../../api";
import {
  createCustomer,
  deleteCustomer,
  listCustomers,
  updateCustomer,
} from "../../services/customers.service";

afterEach(() => {
  vi.restoreAllMocks();
});

describe("customers.service", () => {
  it("loads customers from the plain list endpoint", async () => {
    const apiRequestSpy = vi.spyOn(api, "apiRequest").mockResolvedValue([]);

    await listCustomers();

    expect(apiRequestSpy).toHaveBeenCalledWith({
      method: "GET",
      url: "/customers",
    });
  });

  it("supports create, update and delete operations", async () => {
    const apiRequestSpy = vi.spyOn(api, "apiRequest").mockResolvedValue({});

    await createCustomer({
      name: "Acme",
      email: "ops@acme.com",
      customerSymbol: "ACME",
      notificationsEnabled: true,
      gemFuryUsed: false,
    });

    await updateCustomer("customer-id", { name: "Acme 2" });
    await deleteCustomer("customer-id");

    expect(apiRequestSpy).toHaveBeenNthCalledWith(1, {
      method: "POST",
      url: "/customers",
      data: {
        name: "Acme",
        email: "ops@acme.com",
        customerSymbol: "ACME",
        notificationsEnabled: true,
        gemFuryUsed: false,
      },
    });

    expect(apiRequestSpy).toHaveBeenNthCalledWith(2, {
      method: "PATCH",
      url: "/customers/customer-id",
      data: { name: "Acme 2" },
    });

    expect(apiRequestSpy).toHaveBeenNthCalledWith(3, {
      method: "DELETE",
      url: "/customers/customer-id",
    });
  });
});
