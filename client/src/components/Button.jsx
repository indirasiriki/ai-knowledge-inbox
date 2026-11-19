// Shared button styles so the save, ask, and remove actions look alike.
const variants = {
  primary: 'bg-blue-950 text-white hover:bg-blue-900 disabled:bg-blue-950/40',
  quiet: 'border border-stone-300 bg-white text-stone-700 hover:bg-stone-50 disabled:opacity-50',
  danger: 'border border-red-200 bg-white text-red-800 hover:bg-red-50 disabled:opacity-50',
};

export function Button({
  children,
  variant = 'primary',
  className = '',
  type = 'button',
  ...props
}) {
  return (
    <button
      type={type}
      className={`inline-flex items-center justify-center rounded-md px-3 py-2 text-sm font-medium focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-blue-900/40 focus-visible:ring-offset-1 disabled:cursor-not-allowed ${variants[variant]} ${className}`}
      {...props}
    >
      {children}
    </button>
  );
}
