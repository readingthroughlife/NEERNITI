import React from 'react';
import { cn } from '../../utils/cn';

const Checkbox = React.forwardRef(({ className, ...props }, ref) => (
  <input
    type="checkbox"
    ref={ref}
    className={cn('h-4 w-4 shrink-0 rounded-sm border border-gray-400 focus-visible:ring-2', className)}
    {...props}
  />
));
Checkbox.displayName = 'Checkbox';

export { Checkbox };