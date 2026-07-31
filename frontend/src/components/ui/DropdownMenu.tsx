"use client";

import * as DropdownMenuPrimitive from "@radix-ui/react-dropdown-menu";
import React from "react";

export const DropdownMenu = DropdownMenuPrimitive.Root;
export const DropdownMenuTrigger = DropdownMenuPrimitive.Trigger;
export const DropdownMenuPortal = DropdownMenuPrimitive.Portal;

export const DropdownMenuContent = React.forwardRef<
  HTMLDivElement,
  DropdownMenuPrimitive.DropdownMenuContentProps
>(({ className = "", ...props }, ref) => (
  <DropdownMenuPrimitive.Portal>
    <DropdownMenuPrimitive.Content
      ref={ref}
      className={`z-50 min-w-[8rem] overflow-hidden rounded-md p-1 shadow-md glass-surface text-white outline-none data-[state=open]:animate-in data-[state=closed]:animate-out data-[state=closed]:fade-out-0 data-[state=open]:fade-in-0 data-[state=closed]:zoom-out-95 data-[state=open]:zoom-in-95 ${className}`}
      {...props}
    />
  </DropdownMenuPrimitive.Portal>
));
DropdownMenuContent.displayName = DropdownMenuPrimitive.Content.displayName;

export const DropdownMenuItem = React.forwardRef<
  HTMLDivElement,
  DropdownMenuPrimitive.DropdownMenuItemProps
>(({ className = "", ...props }, ref) => (
  <DropdownMenuPrimitive.Item
    ref={ref}
    className={`relative flex cursor-default select-none items-center rounded-sm px-2 py-1.5 text-sm outline-none transition-colors hover:bg-white/5 focus:bg-white/5 focus:text-white disabled:pointer-events-none disabled:opacity-50 ${className}`}
    {...props}
  />
));
DropdownMenuItem.displayName = DropdownMenuPrimitive.Item.displayName;
