"use client";

import * as TabsPrimitive from "@radix-ui/react-tabs";
import React from "react";

export const Tabs = TabsPrimitive.Root;

export const TabsList = React.forwardRef<
  HTMLDivElement,
  TabsPrimitive.TabsListProps
>(({ className = "", ...props }, ref) => (
  <TabsPrimitive.List
    ref={ref}
    className={`inline-flex h-10 items-center justify-center rounded-md bg-white/5 p-1 text-gray-400 ${className}`}
    {...props}
  />
));
TabsList.displayName = TabsPrimitive.List.displayName;

export const TabsTrigger = React.forwardRef<
  HTMLButtonElement,
  TabsPrimitive.TabsTriggerProps
>(({ className = "", ...props }, ref) => (
  <TabsPrimitive.Trigger
    ref={ref}
    className={`inline-flex items-center justify-center whitespace-nowrap rounded-sm px-3 py-1.5 text-sm font-medium transition-all focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-[#E8B74C] disabled:pointer-events-none disabled:opacity-50 data-[state=active]:bg-white/10 data-[state=active]:text-white ${className}`}
    {...props}
  />
));
TabsTrigger.displayName = TabsPrimitive.Trigger.displayName;

export const TabsContent = React.forwardRef<
  HTMLDivElement,
  TabsPrimitive.TabsContentProps
>(({ className = "", ...props }, ref) => (
  <TabsPrimitive.Content
    ref={ref}
    className={`mt-2 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-[#E8B74C] ${className}`}
    {...props}
  />
));
TabsContent.displayName = TabsPrimitive.Content.displayName;
