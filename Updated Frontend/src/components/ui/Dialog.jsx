import React from 'react';
import * as DialogPrimitive from '@radix-ui/react-dialog';
import { X } from 'lucide-react';
import { cn } from '../../utils/cn';

const Dialog = DialogPrimitive.Root;
const DialogTrigger = DialogPrimitive.Trigger;

const DialogContent = React.forwardRef(({ className, children, ...props }, ref) => (
  <DialogPrimitive.Portal>
    <DialogPrimitive.Overlay className="fixed inset-0 bg-black/50" />
    <DialogPrimitive.Content
      ref={ref}
      className={cn(
        'fixed top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[90vw] max-w-lg bg-white dark:bg-gray-800 p-6 rounded-lg shadow-lg',
        className
      )}
      {...props}
    >
      {children}
    </DialogPrimitive.Content>
  </DialogPrimitive.Portal>
));
DialogContent.displayName = 'DialogContent';

const DialogHeader = ({ className, ...props }) => <div className={cn('flex flex-col space-y-1.5 text-center sm:text-left', className)} {...props} />;
const DialogTitle = React.forwardRef(({ className, ...props }, ref) => <h2 ref={ref} className={cn('text-lg font-semibold', className)} {...props} />);
DialogTitle.displayName = 'DialogTitle';
const DialogDescription = React.forwardRef(({ className, ...props }, ref) => <p ref={ref} className={cn('text-sm text-gray-500 dark:text-gray-400', className)} {...props} />);
DialogDescription.displayName = 'DialogDescription';

export { Dialog, DialogTrigger, DialogContent, DialogHeader, DialogTitle, DialogDescription };