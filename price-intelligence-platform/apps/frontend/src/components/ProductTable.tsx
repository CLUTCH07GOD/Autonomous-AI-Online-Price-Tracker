import { RefreshCw, ExternalLink } from "lucide-react";
import { Product } from "../types";

export function ProductTable({ products, onRefresh }: { products: Product[]; onRefresh: (id: number) => void }) {
  if (products.length === 0) {
    return (
      <div className="flex h-40 items-center justify-center rounded-xl border border-dashed border-neutral-800 text-sm text-neutral-500">
        No tracked products yet.
      </div>
    );
  }

  return (
    <div className="overflow-x-auto rounded-xl border border-white/10 bg-black">
      <table className="w-full text-sm text-left">
        <thead className="bg-neutral-900/80 sticky top-0 backdrop-blur-md z-10 border-b border-white/10 text-xs uppercase tracking-wider text-neutral-400">
          <tr>
            <th className="px-6 py-4 font-medium">Product</th>
            <th className="px-6 py-4 font-medium">Best price</th>
            <th className="px-6 py-4 font-medium">Availability</th>
            <th className="px-6 py-4 font-medium text-right">Actions</th>
          </tr>
        </thead>
        <tbody className="divide-y divide-white/5">
          {products.map((product) => (
            <tr key={product.id} className="group transition-colors hover:bg-white/[0.02]">
              <td className="px-6 py-4">
                <div className="font-semibold text-white line-clamp-1">{product.title}</div>
                <div className="text-xs text-neutral-500 mt-1 flex items-center gap-2">
                  <span className="rounded bg-neutral-800 px-1.5 py-0.5">{product.category || "General"}</span>
                  <span>ID: {product.id}</span>
                </div>
              </td>
              <td className="px-6 py-4">
                <div className="font-bold text-indigo-400">
                  {product.currency} {product.current_best_price ? Number(product.current_best_price).toLocaleString("en-IN") : "-"}
                </div>
                {product.mrp && product.current_best_price && Number(product.mrp) > Number(product.current_best_price) && (
                   <div className="text-xs text-neutral-500 line-through mt-0.5">
                     {product.currency} {Number(product.mrp).toLocaleString("en-IN")}
                   </div>
                )}
              </td>
              <td className="px-6 py-4">
                <span className={`inline-flex items-center gap-1.5 rounded-full px-2 py-1 text-xs font-medium ${product.links[0]?.availability === "In Stock" ? "bg-emerald-500/10 text-emerald-400 border border-emerald-500/20" : "bg-rose-500/10 text-rose-400 border border-rose-500/20"}`}>
                  <span className={`h-1.5 w-1.5 rounded-full ${product.links[0]?.availability === "In Stock" ? "bg-emerald-500" : "bg-rose-500"}`}></span>
                  {product.links[0]?.availability || "Unknown"}
                </span>
              </td>
              <td className="px-6 py-4 text-right">
                <div className="flex items-center justify-end gap-2 opacity-0 group-hover:opacity-100 transition-opacity">
                  {product.links[0]?.url && (
                     <a href={product.links[0].url} target="_blank" rel="noopener noreferrer" className="rounded-lg border border-white/10 bg-neutral-900 p-2 text-neutral-400 hover:bg-neutral-800 hover:text-white transition-colors">
                       <ExternalLink className="h-4 w-4" />
                     </a>
                  )}
                  <button onClick={() => onRefresh(product.id)} className="rounded-lg border border-indigo-500/20 bg-indigo-500/10 p-2 text-indigo-400 hover:bg-indigo-500/20 hover:text-indigo-300 transition-colors" title="Refresh price">
                    <RefreshCw className="h-4 w-4" />
                  </button>
                </div>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
