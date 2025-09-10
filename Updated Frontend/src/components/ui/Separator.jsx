import React from 'react';
import * as SeparatorPrimitive from '@radix-ui/react-separator';
import { cn } from '../../utils/cn';

const Separator = React.forwardRef(({ className, ...props }, ref) => (
  <SeparatorPrimitive.Root ref={ref} className={cn('shrink-0 bg-gray-200 dark:bg-gray-700 h-[1px] w-full', className)} {...props} />
));
Separator.displayName = 'Separator';

export { Separator };