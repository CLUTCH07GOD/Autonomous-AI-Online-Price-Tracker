import React from "react";
import { motion } from "framer-motion";
import { 
  User, 
  Bell, 
  Shield, 
  Cpu, 
  Moon, 
  Sun, 
  Smartphone, 
  Zap, 
  Save, 
  LogOut, 
  Palette, 
  Database, 
  Globe,
  Settings as SettingsIcon,
  CheckCircle2
} from "lucide-react";
import { useTheme } from "../components/ThemeProvider";
import { useAuth } from "../components/AuthContext";
import { cn } from "../lib/utils";

interface SettingsPageProps {
  preferences: any;
  setPreferences: (pref: any) => void;
  onSave: () => void;
}

export function SettingsPage({ preferences, setPreferences, onSave }: SettingsPageProps) {
  const { theme, toggleTheme } = useTheme();
  const { user, logout } = useAuth();

  const sections = [
    { id: "account", label: "Account", icon: User },
    { id: "notifications", label: "Alerts", icon: Bell },
    { id: "appearance", label: "Design", icon: Palette },
    { id: "security", label: "Security", icon: Shield },
    { id: "intelligence", label: "AI & ML", icon: Cpu },
  ];

  const [activeSection, setActiveSection] = React.useState("account");

  return (
    <div className="space-y-8 pb-12">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-3xl font-bold text-white tracking-tight">System Settings</h2>
          <p className="text-neutral-400 mt-1">Configure your price intelligence engine and experience.</p>
        </div>
        <button
          onClick={onSave}
          className="glass-button flex items-center gap-2 rounded-xl px-6 py-3"
        >
          <Save className="h-4 w-4" />
          Save Changes
        </button>
      </div>

      <div className="flex flex-col lg:flex-row gap-8">
        {/* Sidebar Nav */}
        <div className="lg:w-64 flex-shrink-0 space-y-2">
          {sections.map((section) => (
            <button
              key={section.id}
              onClick={() => setActiveSection(section.id)}
              className={cn(
                "w-full flex items-center gap-3 px-4 py-3 rounded-2xl text-sm font-bold transition-all",
                activeSection === section.id
                  ? "bg-indigo-600/20 border border-indigo-500/30 text-white shadow-glow-sm"
                  : "bg-white/[0.03] border border-transparent text-neutral-400 hover:bg-white/[0.06] hover:text-white"
              )}
            >
              <section.icon className="h-5 w-5" />
              {section.label}
            </button>
          ))}
          
          <div className="pt-8">
            <button 
              onClick={logout}
              className="w-full flex items-center gap-3 px-4 py-3 rounded-2xl text-sm font-bold bg-rose-500/10 text-rose-400 border border-rose-500/20 hover:bg-rose-500/20 transition-all"
            >
              <LogOut className="h-5 w-5" />
              Logout Session
            </button>
          </div>
        </div>

        {/* Settings Content */}
        <div className="flex-1 space-y-6">
          <motion.div
            key={activeSection}
            initial={{ opacity: 0, x: 20 }}
            animate={{ opacity: 1, x: 0 }}
            className="glass-card p-10"
          >
            {activeSection === "account" && (
              <div className="space-y-8">
                <div className="flex items-center gap-6">
                  <div className="h-24 w-24 rounded-[2rem] bg-gradient-to-br from-indigo-500 to-purple-600 flex items-center justify-center text-3xl font-black text-white shadow-glow">
                    {user?.name?.[0] || "U"}
                  </div>
                  <div className="space-y-1">
                    <h3 className="text-2xl font-bold text-white">{user?.name}</h3>
                    <p className="text-neutral-500">{user?.email}</p>
                    <div className="flex items-center gap-2 mt-2">
                        <span className="text-[10px] font-black uppercase tracking-widest bg-emerald-500/20 text-emerald-400 px-2 py-1 rounded-md">Pro Member</span>
                        <span className="text-[10px] font-black uppercase tracking-widest bg-white/5 text-neutral-500 px-2 py-1 rounded-md">ID: {user?.id}</span>
                    </div>
                  </div>
                </div>

                <div className="grid grid-cols-1 md:grid-cols-2 gap-6 pt-6">
                  <div className="space-y-2">
                    <label className="text-xs font-bold uppercase tracking-widest text-neutral-500 px-1">Full Name</label>
                    <input 
                        type="text" 
                        defaultValue={user?.name}
                        className="glass-input w-full"
                    />
                  </div>
                  <div className="space-y-2">
                    <label className="text-xs font-bold uppercase tracking-widest text-neutral-500 px-1">Email Address</label>
                    <input 
                        type="email" 
                        defaultValue={user?.email}
                        className="glass-input w-full"
                    />
                  </div>
                </div>
              </div>
            )}

            {activeSection === "appearance" && (
              <div className="space-y-8">
                <div>
                   <h3 className="text-xl font-bold text-white mb-6">Theme Settings</h3>
                   <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
                      {[
                        { id: "dark", label: "Midnight", icon: Moon, desc: "Classic dark mode" },
                        { id: "light", label: "Crystal", icon: Sun, desc: "High contrast light" },
                        { id: "system", label: "Auto", icon: Smartphone, desc: "Follow OS sync" },
                      ].map((t) => (
                        <button
                          key={t.id}
                          onClick={() => t.id !== "system" && theme !== t.id && toggleTheme()}
                          className={cn(
                            "p-6 rounded-3xl border text-left transition-all group",
                            (t.id === theme)
                              ? "bg-indigo-600 border-indigo-400 shadow-glow"
                              : "bg-black/40 border-white/5 hover:border-white/20"
                          )}
                        >
                          <t.icon className={cn("h-6 w-6 mb-4", t.id === theme ? "text-white" : "text-neutral-500 group-hover:text-indigo-400")} />
                          <div className={cn("font-bold", t.id === theme ? "text-white" : "text-neutral-200")}>{t.label}</div>
                          <div className={cn("text-[10px] mt-1", t.id === theme ? "text-indigo-100" : "text-neutral-500")}>{t.desc}</div>
                        </button>
                      ))}
                   </div>
                </div>

                <div>
                   <h3 className="text-xl font-bold text-white mb-6">UI Customization</h3>
                   <div className="space-y-4">
                      <div className="flex items-center justify-between p-4 rounded-2xl bg-black/20 border border-white/5">
                         <div className="flex items-center gap-3">
                            <Zap className="h-5 w-5 text-amber-400" />
                            <div>
                               <div className="text-sm font-bold text-white">Animations</div>
                               <div className="text-xs text-neutral-500">Enable premium Framer Motion effects</div>
                            </div>
                         </div>
                         <div className="h-6 w-11 rounded-full bg-indigo-600 p-1 flex justify-end cursor-pointer"><div className="h-4 w-4 rounded-full bg-white" /></div>
                      </div>
                      <div className="flex items-center justify-between p-4 rounded-2xl bg-black/20 border border-white/5">
                         <div className="flex items-center gap-3">
                            <Database className="h-5 w-5 text-indigo-400" />
                            <div>
                               <div className="text-sm font-bold text-white">Dense Layout</div>
                               <div className="text-xs text-neutral-500">Show more data cards per row</div>
                            </div>
                         </div>
                         <div className="h-6 w-11 rounded-full bg-neutral-800 p-1 flex justify-start cursor-pointer"><div className="h-4 w-4 rounded-full bg-neutral-600" /></div>
                      </div>
                   </div>
                </div>
              </div>
            )}

            {activeSection === "intelligence" && (
                <div className="space-y-8">
                    <h3 className="text-xl font-bold text-white mb-6 flex items-center gap-2">
                        <Cpu className="h-6 w-6 text-indigo-400" />
                        AI Analysis Preferences
                    </h3>
                    
                    <div className="space-y-6">
                        <div className="space-y-3">
                            <label className="text-sm font-bold text-white">Price Sensitivity ({preferences?.sensitivity || 5}%)</label>
                            <input 
                                type="range" 
                                min="1" 
                                max="20" 
                                value={preferences?.sensitivity || 5}
                                onChange={(e) => setPreferences({...preferences, sensitivity: parseInt(e.target.value)})}
                                className="w-full h-2 bg-neutral-800 rounded-lg appearance-none cursor-pointer accent-indigo-500" 
                            />
                            <div className="flex justify-between text-[10px] font-bold text-neutral-600 uppercase tracking-widest">
                                <span>High Precision</span>
                                <span>High Volume</span>
                            </div>
                        </div>

                        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                            <div className="p-4 rounded-2xl bg-black/20 border border-white/5 flex flex-col justify-between">
                                <div className="text-sm font-bold text-white mb-1">Anomaly Detection</div>
                                <div className="text-xs text-neutral-500 mb-4">Automatically flag suspicious price jumps</div>
                                <button className="text-[10px] font-bold uppercase tracking-widest text-emerald-400 flex items-center gap-1">
                                    <CheckCircle2 className="h-3 w-3" /> Enabled
                                </button>
                            </div>
                            <div className="p-4 rounded-2xl bg-black/20 border border-white/5 flex flex-col justify-between">
                                <div className="text-sm font-bold text-white mb-1">Deep Scan</div>
                                <div className="text-xs text-neutral-500 mb-4">Daily full-retailer marketplace audit</div>
                                <button className="text-[10px] font-bold uppercase tracking-widest text-neutral-500">Enable Pro</button>
                            </div>
                        </div>
                    </div>
                </div>
            )}

            {/* Other sections would go here... */}
            {["notifications", "security"].includes(activeSection) && (
              <div className="flex flex-col items-center justify-center py-20 text-neutral-600">
                  <SettingsIcon className="h-12 w-12 mb-4 opacity-10 animate-spin-slow" />
                  <p className="font-bold uppercase tracking-[0.2em] text-xs">Module Coming Soon</p>
              </div>
            )}
          </motion.div>
        </div>
      </div>
    </div>
  );
}
