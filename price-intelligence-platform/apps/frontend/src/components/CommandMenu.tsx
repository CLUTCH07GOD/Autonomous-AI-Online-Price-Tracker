import * as React from "react";
import {
  CommandDialog,
  CommandEmpty,
  CommandGroup,
  CommandInput,
  CommandItem,
  CommandList,
  CommandSeparator,
} from "./ui/command";
import { 
  LayoutDashboard, 
  Search, 
  BarChart3, 
  ArrowLeftRight, 
  TrendingDown, 
  Percent, 
  Zap, 
  Map, 
  History, 
  Bell, 
  Settings,
  BrainCircuit,
  BookOpen
} from "lucide-react";

export function CommandMenu({ 
  setActive, 
  products 
}: { 
  setActive: (page: string) => void,
  products: any[]
}) {
  const [open, setOpen] = React.useState(false);

  React.useEffect(() => {
    const down = (e: KeyboardEvent) => {
      if (e.key === "k" && (e.metaKey || e.ctrlKey)) {
        e.preventDefault();
        setOpen((open) => !open);
      }
    };
    document.addEventListener("keydown", down);
    return () => document.removeEventListener("keydown", down);
  }, []);

  const runCommand = (command: () => void) => {
    setOpen(false);
    command();
  };

  const pages = [
    { name: "Dashboard", icon: LayoutDashboard },
    { name: "Product Search", icon: Search },
    { name: "AI Insights", icon: BrainCircuit },
    { name: "Comparison", icon: ArrowLeftRight },
    { name: "Trend Analytics", icon: BarChart3 },
    { name: "Fake Discount Detector", icon: Percent },
    { name: "Recommendation Center", icon: Zap },
    { name: "Price Heatmaps", icon: Map },
    { name: "Historical Analytics", icon: History },
    { name: "Smart Alerts", icon: Bell },
    { name: "Settings", icon: Settings },
    { name: "References", icon: BookOpen },
  ];

  return (
    <>
      <button
        onClick={() => setOpen(true)}
        className="group flex h-10 w-full items-center gap-2 rounded-xl border border-white/[0.06] bg-white/[0.02] px-4 text-sm font-medium text-neutral-500 transition-all hover:bg-white/[0.05] hover:text-white hover:border-white/[0.1] backdrop-blur-sm"
      >
        <Search className="h-4 w-4" />
        <span className="flex-1 text-left">Search anything...</span>
        <kbd className="pointer-events-none flex h-5 select-none items-center gap-1 rounded border border-white/10 bg-black px-1.5 font-mono text-[10px] font-medium opacity-100 group-hover:border-white/20">
          <span className="text-xs">⌘</span>K
        </kbd>
      </button>
      <CommandDialog open={open} onOpenChange={setOpen}>
        <CommandInput placeholder="Type a command or search products..." />
        <CommandList>
          <CommandEmpty>No results found.</CommandEmpty>
          <CommandGroup heading="Navigation">
            {pages.map((page) => (
              <CommandItem
                key={page.name}
                onSelect={() => runCommand(() => setActive(page.name))}
              >
                <page.icon className="mr-2 h-4 w-4" />
                <span>{page.name}</span>
              </CommandItem>
            ))}
          </CommandGroup>
          <CommandSeparator />
          {products.length > 0 && (
            <CommandGroup heading="Recent Products">
              {products.slice(0, 5).map((product) => (
                <CommandItem
                  key={product.id}
                  onSelect={() => runCommand(() => {
                    setActive("Product Search");
                    // In a real app we might want to deep link to the product
                  })}
                >
                   <div className="mr-2 flex h-4 w-4 items-center justify-center overflow-hidden rounded bg-white">
                     {product.image_url ? (
                       <img src={product.image_url} alt="" className="h-full w-full object-contain" />
                     ) : (
                       <div className="bg-neutral-200 w-full h-full" />
                     )}
                   </div>
                   <span className="line-clamp-1">{product.title}</span>
                </CommandItem>
              ))}
            </CommandGroup>
          )}
        </CommandList>
      </CommandDialog>
    </>
  );
}
