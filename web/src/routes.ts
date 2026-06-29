import { Role } from "./api";

export type Section = "admin" | "driver" | "maintenance" | "finance" | "recycling";

export const roleHome: Record<Role, `/${Section}`> = {
  "Sistem Yoneticisi": "/admin",
  Sofor: "/driver",
  "Bakim Teknisyeni": "/maintenance",
  "Muhasebe Personeli": "/finance",
  "Geri Donusum Operatoru": "/recycling",
};

export const sectionLabels: Record<Section, string> = {
  admin: "Yonetim Merkezi",
  driver: "Sofor Operasyon",
  maintenance: "Bakim Operasyon",
  finance: "Muhasebe Paneli",
  recycling: "Geri Donusum Tesisi",
};

export function sectionFromPath(pathname: string): Section | null {
  const first = pathname.split("/").filter(Boolean)[0] as Section | undefined;
  if (!first) return null;
  return ["admin", "driver", "maintenance", "finance", "recycling"].includes(first)
    ? first
    : null;
}
