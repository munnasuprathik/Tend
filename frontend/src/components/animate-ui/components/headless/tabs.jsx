'use client';

import * as React from 'react';
import { cn } from '@/lib/utils';

const TabGroupContext = React.createContext({
  selectedValue: null,
  setSelectedValue: () => {},
});

const TabGroup = ({ defaultValue, value, onChange, children, className, ...props }) => {
  const [selectedValue, setSelectedValue] = React.useState(() => {
    if (value !== undefined) return value;
    if (defaultValue !== undefined) return defaultValue;
    return null;
  });

  const controlledValue = value !== undefined ? value : selectedValue;
  const handleChange = React.useCallback((newValue) => {
    if (value === undefined) {
      setSelectedValue(newValue);
    }
    if (onChange) {
      onChange(newValue);
    }
  }, [value, onChange]);

  return (
    <TabGroupContext.Provider value={{ selectedValue: controlledValue, setSelectedValue: handleChange }}>
      <div className={cn('w-full', className)} {...props}>
        {children}
      </div>
    </TabGroupContext.Provider>
  );
};

const TabList = React.forwardRef(({ className, children, ...props }, ref) => {
  return (
    <div
      ref={ref}
      className={cn(
        'inline-flex h-9 items-center justify-center rounded-lg bg-muted p-1 text-muted-foreground',
        className
      )}
      role="tablist"
      {...props}
    >
      {children}
    </div>
  );
});
TabList.displayName = 'TabList';

const Tab = React.forwardRef(({ index, value, className, children, ...props }, ref) => {
  const { selectedValue, setSelectedValue } = React.useContext(TabGroupContext);
  const tabValue = value !== undefined ? value : (index !== undefined ? index : null);
  const isSelected = selectedValue === tabValue;

  if (tabValue === null) {
    console.warn('Tab component requires either a value or index prop');
    return null;
  }

  return (
    <button
      ref={ref}
      role="tab"
      aria-selected={isSelected}
      onClick={() => setSelectedValue(tabValue)}
      className={cn(
        'inline-flex items-center justify-center whitespace-nowrap rounded-md px-3 py-1 text-sm font-medium ring-offset-background transition-all focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:pointer-events-none disabled:opacity-50',
        isSelected
          ? 'bg-background text-foreground shadow'
          : 'text-muted-foreground hover:text-foreground hover:bg-accent/50',
        className
      )}
      {...props}
    >
      {children}
    </button>
  );
});
Tab.displayName = 'Tab';

const TabPanels = React.forwardRef(({ className, children, ...props }, ref) => {
  return (
    <div ref={ref} className={cn('mt-2', className)} {...props}>
      {children}
    </div>
  );
});
TabPanels.displayName = 'TabPanels';

const TabPanel = React.forwardRef(({ index, value, className, children, ...props }, ref) => {
  const { selectedValue } = React.useContext(TabGroupContext);
  const panelValue = value !== undefined ? value : (index !== undefined ? index : null);
  const isSelected = selectedValue === panelValue;

  if (panelValue === null) {
    console.warn('TabPanel component requires either a value or index prop');
    return null;
  }

  if (!isSelected) return null;

  return (
    <div
      ref={ref}
      role="tabpanel"
      className={className}
      {...props}
    >
      {children}
    </div>
  );
});
TabPanel.displayName = 'TabPanel';

export { TabGroup, TabList, Tab, TabPanels, TabPanel };

