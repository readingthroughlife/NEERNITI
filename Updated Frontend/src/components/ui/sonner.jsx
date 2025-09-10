import { Toaster as Sonner } from 'sonner';

const Toaster = ({...props}) => {
  return (
    <Sonner
      className="toaster group"
      toastOptions={{
        classNames: {
          toast: 'group toast group-[.toaster]:bg-white group-[.toaster]:text-gray-900 group-[.toaster]:border-gray-200 group-[.toaster]:shadow-lg dark:group-[.toaster]:bg-gray-800 dark:group-[.toaster]:text-white dark:group-[.toaster]:border-gray-700',
          description: 'group-[.toast]:text-gray-500 dark:group-[.toast]:text-gray-400',
          actionButton: 'group-[.toast]:bg-blue-600 group-[.toast]:text-white',
          cancelButton: 'group-[.toast]:bg-gray-200 group-[.toast]:text-gray-900',
        },
      }}
      {...props}
    />
  );
};

export { Toaster };