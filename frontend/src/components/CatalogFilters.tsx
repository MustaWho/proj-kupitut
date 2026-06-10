import type { Category, ProductFilters } from "../types";

type CatalogFiltersProps = {
  categories: Category[];
  filters: ProductFilters;
  onChange: (filters: ProductFilters) => void;
};

export function CatalogFilters({ categories, filters, onChange }: CatalogFiltersProps) {
  return (
    <form className="filters" onSubmit={(event) => event.preventDefault()}>
      <input
        aria-label="Поиск"
        placeholder="Поиск по товарам"
        value={filters.search ?? ""}
        onChange={(event) => onChange({ ...filters, search: event.target.value })}
      />
      <select
        aria-label="Категория"
        value={filters.categoryId ?? ""}
        onChange={(event) =>
          onChange({
            ...filters,
            categoryId: event.target.value ? Number(event.target.value) : undefined
          })
        }
      >
        <option value="">Все категории</option>
        {categories.map((category) => (
          <option key={category.id} value={category.id}>
            {category.name}
          </option>
        ))}
      </select>
      <input
        aria-label="Цена от"
        type="number"
        min="0"
        placeholder="Цена от"
        value={filters.minPrice ?? ""}
        onChange={(event) =>
          onChange({
            ...filters,
            minPrice: event.target.value ? Number(event.target.value) : undefined
          })
        }
      />
      <input
        aria-label="Цена до"
        type="number"
        min="0"
        placeholder="Цена до"
        value={filters.maxPrice ?? ""}
        onChange={(event) =>
          onChange({
            ...filters,
            maxPrice: event.target.value ? Number(event.target.value) : undefined
          })
        }
      />
      <select
        aria-label="Рейтинг"
        value={filters.minRating ?? ""}
        onChange={(event) =>
          onChange({
            ...filters,
            minRating: event.target.value ? Number(event.target.value) : undefined
          })
        }
      >
        <option value="">Любой рейтинг</option>
        <option value="4">От 4</option>
        <option value="3">От 3</option>
      </select>
    </form>
  );
}
