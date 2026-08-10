import {
  collections,
  marketplaceName,
  plugins,
  site,
  totals,
} from "../catalog.generated";

export const dynamic = "force-dynamic";

export function GET() {
  return Response.json(
    {
      name: site.name,
      identity: site.identity,
      description: site.description,
      marketplace: marketplaceName,
      counts: totals,
      collections,
      plugins,
    },
    { headers: { "cache-control": "no-store" } },
  );
}
