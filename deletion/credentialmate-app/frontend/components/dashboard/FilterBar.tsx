/**
 * Reusable Filter Bar Component
 *
 * Provides filtering controls for dashboards.
 *
 * @author Claude Code
 * @session MOCK-DASH-001
 */

export interface FilterOption {
  label: string
  value: string
}

export interface FilterBarProps {
  searchQuery: string
  onSearchChange: (query: string) => void
  filters: {
    label: string
    value: string
    options: FilterOption[]
    onChange: (value: string) => void
  }[]
  activeFiltersCount: number
  onClearFilters: () => void
}

export function FilterBar({
  searchQuery,
  onSearchChange,
  filters,
  activeFiltersCount,
  onClearFilters,
}: FilterBarProps) {
  return (
    <div className="bg-white rounded-lg shadow p-6">
      <div className="flex items-center justify-between mb-4">
        <div className="flex items-center space-x-2">
          <h3 className="font-bold text-lg">🔍 Filters & Search</h3>
          {activeFiltersCount > 0 && (
            <span className="bg-blue-600 text-white text-xs px-2 py-1 rounded-full">
              {activeFiltersCount} active
            </span>
          )}
        </div>
        {activeFiltersCount > 0 && (
          <button
            onClick={onClearFilters}
            className="text-sm text-blue-600 hover:text-blue-800 font-medium"
          >
            Clear all filters
          </button>
        )}
      </div>

      {/* Search Bar */}
      <div className="mb-4">
        <input
          type="text"
          placeholder="🔍 Search..."
          value={searchQuery}
          onChange={(e) => onSearchChange(e.target.value)}
          className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
        />
      </div>

      {/* Filter Dropdowns */}
      <div className={`grid grid-cols-1 md:grid-cols-${Math.min(filters.length, 5)} gap-4`}>
        {filters.map((filter, idx) => (
          <div key={idx}>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              {filter.label}
            </label>
            <select
              value={filter.value}
              onChange={(e) => filter.onChange(e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
            >
              {filter.options.map(option => (
                <option key={option.value} value={option.value}>
                  {option.label}
                </option>
              ))}
            </select>
          </div>
        ))}
      </div>
    </div>
  )
}
