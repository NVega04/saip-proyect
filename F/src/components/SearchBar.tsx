import { useRef, useState, useEffect } from "react";
import "./SearchBar.css";

export type SortOrder    = "asc" | "desc" | null;
export type SortCriteria = "id" | "alpha";

interface SearchBarProps {
  value: string;
  onChange: (value: string) => void;
  placeholder?: string;
  sortOrder?:    SortOrder;
  sortCriteria?: SortCriteria;
  onSort?: (order: SortOrder, criteria: SortCriteria) => void;
}

export default function SearchBar({
  value,
  onChange,
  placeholder = "Buscar",
  sortOrder    = null,
  sortCriteria = "id",
  onSort,
}: SearchBarProps) {
  const [open, setOpen] = useState(false);
  const ref = useRef<HTMLDivElement>(null);

  useEffect(() => {
  const handler = (e: MouseEvent) => {
    if (ref.current && !ref.current.contains(e.target as Node)) 
      setOpen(false);
  };
  document.addEventListener("mousedown", handler);
  return () => document.removeEventListener("mousedown", handler);
}, []);
  
  const select = (order: SortOrder, criteria: SortCriteria) => {
  onSort?.(order, criteria);
  setOpen(false);
};

  const FilterIcon = () => {
    if (sortOrder === "asc")  return (
      <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="#7d5a3c" strokeWidth="2">
        <line x1="12" y1="19" x2="12" y2="5"/><polyline points="5 12 12 5 19 12"/>
      </svg>
    );
    if (sortOrder === "desc") return (
      <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="#7d5a3c" strokeWidth="2">
        <line x1="12" y1="5" x2="12" y2="19"/><polyline points="19 12 12 19 5 12"/>
      </svg>
    );
    return (
   <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="#7d5a3c" strokeWidth="2">
     <line x1="3" y1="5"  x2="21" y2="5"/>
     <line x1="3" y1="10" x2="16" y2="10"/>
     <line x1="3" y1="15" x2="11" y2="15"/>
     <line x1="3" y1="20" x2="7"  y2="20"/>
   </svg>
  );
  };

  const isActive = (order: SortOrder, criteria: SortCriteria) =>
    sortOrder === order && sortCriteria === criteria;
  
  return (
    <div className="searchbar">
      <div className="searchbar__input-wrapper">
        <svg className="searchbar__icon" width="14" height="14" viewBox="0 0 24 24"
          fill="none" stroke="#9e7e62" strokeWidth="2">
          <circle cx="11" cy="11" r="8" />
          <line x1="21" y1="21" x2="16.65" y2="16.65" />
        </svg>
        <input
          type="text"
          value={value}
          onChange={(e) => onChange(e.target.value)}
          placeholder={placeholder}
          className="searchbar__input"
        />
      </div>
           {onSort && (
        <div className="searchbar__sort-wrapper" ref={ref}>
          <button
            className={`searchbar__filter-btn ${sortOrder ? "searchbar__filter-btn--active" : ""}`}
            onClick={() => setOpen((o) => !o)}
            type="button"
            title="Ordenar"
          >
            <FilterIcon />
          </button>

          {open && (
            <div className="sort-dropdown">
              <p className="sort-dropdown__label">Ordenar por ID</p>
              <button
                className={`sort-dropdown__item ${isActive("asc",  "id") ? "sort-dropdown__item--selected" : ""}`}
                onClick={() => select("asc",  "id")}
              >
                <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                  <line x1="12" y1="19" x2="12" y2="5"/><polyline points="5 12 12 5 19 12"/>
                </svg>
                ASC
              </button>
              <button
                className={`sort-dropdown__item ${isActive("desc", "id") ? "sort-dropdown__item--selected" : ""}`}
                onClick={() => select("desc", "id")}
              >
                <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                  <line x1="12" y1="5" x2="12" y2="19"/><polyline points="19 12 12 19 5 12"/>
                </svg>
                DESC
              </button>

              <div className="sort-dropdown__divider" />

              <p className="sort-dropdown__label">Ordenar alfabéticamente</p>
              <button
                className={`sort-dropdown__item ${isActive("asc",  "alpha") ? "sort-dropdown__item--selected" : ""}`}
                onClick={() => select("asc",  "alpha")}
              >
                <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                  <line x1="12" y1="19" x2="12" y2="5"/><polyline points="5 12 12 5 19 12"/>
                </svg>
                A → Z
              </button>
              <button
                className={`sort-dropdown__item ${isActive("desc", "alpha") ? "sort-dropdown__item--selected" : ""}`}
                onClick={() => select("desc", "alpha")}
              >
                <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                  <line x1="12" y1="5" x2="12" y2="19"/><polyline points="19 12 12 19 5 12"/>
                </svg>
                Z → A
              </button>
            </div>
          )}
        </div>
      )}
    </div>
  );
}
