import { render, screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { Modal } from "../../components/modals";

describe("Modal", () => {
  it("renders through a portal attached to document.body", async () => {
    const { container } = render(
      <div data-testid="local-root">
        <Modal title="Test modal" onClose={() => undefined}>
          <p>Modal content</p>
        </Modal>
      </div>,
    );

    expect(
      await screen.findByRole("dialog", { name: "Test modal" }),
    ).toBeInTheDocument();
    expect(document.body.querySelector(".lm-modal__backdrop")).not.toBeNull();
    expect(container.querySelector(".lm-modal__backdrop")).toBeNull();
  });
});
