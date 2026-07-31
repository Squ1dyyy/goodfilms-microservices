"use client";

import * as React from "react";
import * as ToastPrimitives from "@radix-ui/react-toast";

export const ToastProvider = ToastPrimitives.Provider;

export const ToastViewport = React.forwardRef<
  HTMLOListElement,
  ToastPrimitives.ToastViewportProps
>(({ className = "", ...props }, ref) => (
  <ToastPrimitives.Viewport
    ref={ref}
    className={`fixed bottom-0 right-0 z-[100] flex max-h-screen w-full flex-col-reverse p-4 md:max-w-[420px] ${className}`}
    {...props}
  />
));
ToastViewport.displayName = ToastPrimitives.Viewport.displayName;

export const Toast = React.forwardRef<
  HTMLLIElement,
  ToastPrimitives.ToastProps
>(({ className = "", ...props }, ref) => (
  <ToastPrimitives.Root
    ref={ref}
    className={`group pointer-events-auto relative flex w-full items-center justify-between space-x-4 overflow-hidden rounded-md p-6 pr-8 shadow-lg transition-all data-[swipe=cancel]:translate-x-0 data-[swipe=end]:translate-x-[var(--radix-toast-swipe-end-x)] data-[swipe=move]:translate-x-[var(--radix-toast-swipe-move-x)] data-[swipe=move]:transition-none data-[state=open]:animate-in data-[state=closed]:animate-out data-[swipe=end]:animate-out data-[state=closed]:fade-out-80 data-[state=open]:slide-in-from-bottom-full data-[state=closed]:slide-out-to-right-full glass-surface text-white ${className}`}
    {...props}
  />
));
Toast.displayName = ToastPrimitives.Root.displayName;

export const ToastTitle = React.forwardRef<
  HTMLDivElement,
  ToastPrimitives.ToastTitleProps
>(({ className = "", ...props }, ref) => (
  <ToastPrimitives.Title
    ref={ref}
    className={`text-sm font-semibold ${className}`}
    {...props}
  />
));
ToastTitle.displayName = ToastPrimitives.Title.displayName;

export const ToastDescription = React.forwardRef<
  HTMLDivElement,
  ToastPrimitives.ToastDescriptionProps
>(({ className = "", ...props }, ref) => (
  <ToastPrimitives.Description
    ref={ref}
    className={`text-sm opacity-90 ${className}`}
    {...props}
  />
));
ToastDescription.displayName = ToastPrimitives.Description.displayName;

export const ToastClose = React.forwardRef<
  HTMLButtonElement,
  ToastPrimitives.ToastCloseProps
>(({ className = "", ...props }, ref) => (
  <ToastPrimitives.Close
    ref={ref}
    className={`absolute right-2 top-2 rounded-md p-1 text-white/50 opacity-0 transition-opacity hover:text-white focus:opacity-100 focus:outline-none focus:ring-2 group-hover:opacity-100 ${className}`}
    toast-close=""
    {...props}
  >
    &#x2715;
  </ToastPrimitives.Close>
));
ToastClose.displayName = ToastPrimitives.Close.displayName;
