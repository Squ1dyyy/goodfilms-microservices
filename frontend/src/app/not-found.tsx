import Link from "next/link";
import { Button } from "@/components/ui/Button";
import { GlassPanel } from "@/components/glass/GlassPanel";
import { LiquidBlobBackground } from "@/components/glass/LiquidBlobBackground";

export default function NotFound() {
  return (
    <div className="relative min-h-screen flex items-center justify-center p-4">
      <LiquidBlobBackground />
      <GlassPanel className="max-w-md text-center space-y-6">
        <h1 className="text-6xl font-extrabold text-white font-display">404</h1>
        <h2 className="text-2xl font-bold text-white">Страница не найдена</h2>
        <p className="text-gray-400">
          Запрашиваемый фильм, персона или раздел не найдены или были удалены.
        </p>
        <Link href="/" className="inline-block mt-4">
          <Button>Вернуться на главную</Button>
        </Link>
      </GlassPanel>
    </div>
  );
}
