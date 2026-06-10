import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { describe, expect, it, vi } from "vitest";
import { CatalogFilters } from "./CatalogFilters";

describe("CatalogFilters", () => {
  it("обновляет фильтры поиска и категории", async () => {
    const onChange = vi.fn();
    const user = userEvent.setup();

    render(
      <CatalogFilters
        categories={[{ id: 7, name: "Электроника" }]}
        filters={{}}
        onChange={onChange}
      />
    );

    await user.type(screen.getByLabelText("Поиск"), "phone");
    expect(onChange).toHaveBeenCalledWith({ search: "p" });

    await user.selectOptions(screen.getByLabelText("Категория"), "7");
    expect(onChange).toHaveBeenCalledWith({ categoryId: 7 });
  });
});
