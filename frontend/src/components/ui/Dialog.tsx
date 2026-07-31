"use client";

import * as DialogPrimitive from "@radix-ui/react-dialog";
import React from "react";

export const Dialog = DialogPrimitive.Root;
export const DialogTrigger = DialogPrimitive.Trigger;
export const DialogPortal = DialogPrimitive.Portal;

export const DialogOverlay = React.forwardRef<
  HTMLDivElement,
  DialogPrimitive.DialogOverlayProps
>(({ className = "", ...props }, ref) => (
  <DialogPrimitive.Overlay
    ref={ref}
    className={`fixed inset-0 z-50 bg-[#0A0C14]/80 backdrop-blur-sm data-[state=open]:animate-in data-[state=closed]:animate-out data-[state=closed]:fade-out-0 data-[state=open]:fade-in-0 ${className}`}
    {...props}
  />
));
DialogOverlay.displayName = DialogPrimitive.Overlay.displayName;

export const DialogContent = React.forwardRef<
  HTMLDivElement,
  DialogPrimitive.DialogContentProps
>(({ className = "", children, ...props }, ref) => (
  <DialogPortal>
    <DialogOverlay />
    <DialogPrimitive.Content
      ref={ref}
      className={`fixed left-[50%] top-[50%] z-50 grid w-full max-w-lg translate-x-[-50%] translate-y-[-50%] gap-4 p-6 glass-surface rounded-xl duration-200 data-[state=open]:animate-in data-[state=closed]:animate-out data-[state=closed]:fade-out-0 data-[state=open]:fade-in-0 data-[state=closed]:zoom-out-95 data-[state=open]:zoom-in-95 data-[state=closed]:slide-out-to-left-1/2 data-[state=closed]:slide-out-to-top-[48%] data-[state=open]:slide-in-from-left-1/2 data-[state=open]:slide-in-from-top-[48%] outline-none focus:ring-2 focus:ring-[#E8B74C] ${className}`}
      {...props}
    >
      {children}
    </DialogPrimitive.Content>
  </DialogPortal>
));
DialogContent.displayName = DialogPrimitive.Content.displayName;

export const DialogHeader = ({
  className = "",
  ...props
}: React.HTMLAttributes<HTMLDivElement>) => (
  <div
    className={`flex flex-col space-y-1.5 text-center sm:text-left ${className}`}
    {...props}
  />
);
DialogHeader.displayName = "DialogHeader";

export const DialogTitle = React.forwardRef<
  HTMLHeadingElement,
  DialogPrimitive.DialogTitleProps
>(({ className = "", ...props }, ref) => (
  <DialogPrimitive.Title
    ref={ref}
    className={`text-lg font-semibold leading-none tracking-tight text-white ${className}`}
    {...props}
  />
));
DialogTitle.displayName = DialogPrimitive.Title.displayName;

export const DialogDescription = React.forwardRef<
  HTMLParagraphElement,
  DialogPrimitive.DialogDescriptionProps
>(({ className = "", ...props }, ref) => (
  <DialogPrimitive.Description
    ref={ref}
    className={`text-sm text-gray-400 ${className}`}
    {...props}
  />
));
DialogDescription.displayName = DialogPrimitive.Description.displayName;
