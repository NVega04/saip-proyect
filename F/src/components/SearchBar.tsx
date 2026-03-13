import "./SearchBar.css";

interface SearchBarProps {
  value: string;
  onChange: (value: string) => void;
  placeholder?: string;
  onFilter?: () => void;
}

export default function SearchBar({
  value,
  onChange,
  placeholder = "Buscar",
  onFilter,
}: SearchBarProps) {
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
      {onFilter && (
        <button className="searchbar__filter-btn" onClick={onFilter} type="button">
          <svg width="15" height="15" viewBox="0 0 24 24"
            fill="none" stroke="#7d5a3c" strokeWidth="2">
            <polygon points="22 3 2 3 10 12.46 10 19 14 21 14 12.46 22 3" />
          </svg>
        </button>
      )}
    </div>
  );
}
