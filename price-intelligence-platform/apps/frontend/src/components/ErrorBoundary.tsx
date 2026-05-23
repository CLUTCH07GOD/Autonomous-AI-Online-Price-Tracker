import React from "react";
import { AlertTriangle, RefreshCcw } from "lucide-react";

type Props = {
  children: React.ReactNode;
};

type State = {
  error?: Error;
};

export class ErrorBoundary extends React.Component<Props, State> {
  state: State = {};

  static getDerivedStateFromError(error: Error): State {
    return { error };
  }

  componentDidCatch(error: Error, info: React.ErrorInfo) {
    console.error("[UI] Render failure", error, info.componentStack);
  }

  render() {
    if (!this.state.error) return this.props.children;

    return (
      <div className="min-h-screen bg-[#06060f] text-neutral-100 flex items-center justify-center p-6">
        <div className="max-w-md rounded-2xl border border-rose-500/20 bg-rose-500/10 p-6 text-center">
          <AlertTriangle className="mx-auto h-8 w-8 text-rose-300" />
          <h1 className="mt-4 text-lg font-bold text-white">Something could not render</h1>
          <p className="mt-2 text-sm text-neutral-300">{this.state.error.message || "The page hit an unexpected UI error."}</p>
          <button
            className="mt-5 inline-flex items-center gap-2 rounded-xl border border-white/10 bg-white/10 px-4 py-2 text-sm font-semibold text-white"
            onClick={() => this.setState({ error: undefined })}
          >
            <RefreshCcw className="h-4 w-4" />
            Retry view
          </button>
        </div>
      </div>
    );
  }
}
