import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { describe, expect, it } from "vitest";
import {
  Link,
  Outlet,
  createMemoryRouter,
  RouterProvider,
} from "react-router-dom";
import { PageTransition } from "../../components/common";

function Layout() {
  return (
    <div>
      <nav>
        <Link to="/">Dashboard</Link>
        <Link to="/customers">Customers</Link>
      </nav>
      <PageTransition>
        <Outlet />
      </PageTransition>
    </div>
  );
}

describe("PageTransition", () => {
  it("applies the enter animation on route change", async () => {
    const user = userEvent.setup();
    const router = createMemoryRouter(
      [
        {
          path: "/",
          element: <Layout />,
          children: [
            {
              index: true,
              element: <h1>Dashboard</h1>,
            },
            {
              path: "customers",
              element: <h1>Customers</h1>,
            },
          ],
        },
      ],
      {
        initialEntries: ["/"],
      },
    );

    const { container } = render(<RouterProvider router={router} />);

    expect(
      await screen.findByRole("heading", { name: "Dashboard" }),
    ).toBeInTheDocument();
    expect(container.querySelector(".animate-page-enter")).not.toBeNull();

    await user.click(screen.getByRole("link", { name: "Customers" }));

    expect(
      await screen.findByRole("heading", { name: "Customers" }),
    ).toBeInTheDocument();
    expect(container.querySelector(".animate-page-enter")).not.toBeNull();
  });
});
