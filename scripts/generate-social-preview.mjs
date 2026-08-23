import sharp from "sharp";

const width = 1200;
const height = 630;

const svg = `
<svg width="${width}" height="${height}" viewBox="0 0 ${width} ${height}" xmlns="http://www.w3.org/2000/svg">
  <rect width="1200" height="630" fill="#F8F5EF"/>
  <rect x="54" y="54" width="58" height="58" fill="#B33C49"/>
  <text x="83" y="90" text-anchor="middle" fill="#FCFBF8" font-family="ui-monospace, SFMono-Regular, Menlo, monospace" font-size="20" font-weight="700">AP</text>
  <text x="136" y="77" fill="#292729" font-family="Avenir Next, Helvetica Neue, Arial, sans-serif" font-size="17" font-weight="700" letter-spacing="2">COMMUNITY AGENT PLUGINS</text>
  <text x="136" y="101" fill="#6B6864" font-family="Avenir Next, Helvetica Neue, Arial, sans-serif" font-size="14" letter-spacing="1">PUBLIC REGISTRY · MAIN BRANCH</text>
  <line x1="54" y1="137" x2="1146" y2="137" stroke="#DEDAD3"/>
  <text x="54" y="252" fill="#292729" font-family="Georgia, Times New Roman, serif" font-size="70">Choose the work.</text>
  <text x="54" y="330" fill="#292729" font-family="Georgia, Times New Roman, serif" font-size="70">Check the host.</text>
  <text x="54" y="408" fill="#292729" font-family="Georgia, Times New Roman, serif" font-size="70">Install the plugin.</text>
  <text x="925" y="236" fill="#292729" font-family="ui-monospace, SFMono-Regular, Menlo, monospace" font-size="52">21</text>
  <text x="925" y="268" fill="#6B6864" font-family="Avenir Next, Helvetica Neue, Arial, sans-serif" font-size="15">PUBLIC PLUGINS</text>
  <text x="925" y="354" fill="#292729" font-family="ui-monospace, SFMono-Regular, Menlo, monospace" font-size="52">160</text>
  <text x="925" y="386" fill="#6B6864" font-family="Avenir Next, Helvetica Neue, Arial, sans-serif" font-size="15">BUNDLED SKILLS</text>
  <line x1="54" y1="476" x2="1146" y2="476" stroke="#DEDAD3"/>
  <rect x="54" y="514" width="232" height="16" fill="#FFDD00"/>
  <rect x="308" y="514" width="232" height="16" fill="#00B49B"/>
  <rect x="562" y="514" width="232" height="16" fill="#E2625E"/>
  <rect x="816" y="514" width="330" height="16" fill="#004F46"/>
  <text x="54" y="562" fill="#6B6864" font-family="Avenir Next, Helvetica Neue, Arial, sans-serif" font-size="14">BUILD &amp; CREATE</text>
  <text x="308" y="562" fill="#6B6864" font-family="Avenir Next, Helvetica Neue, Arial, sans-serif" font-size="14">PLAN &amp; RUN</text>
  <text x="562" y="562" fill="#6B6864" font-family="Avenir Next, Helvetica Neue, Arial, sans-serif" font-size="14">VERIFY &amp; GOVERN</text>
  <text x="816" y="562" fill="#6B6864" font-family="Avenir Next, Helvetica Neue, Arial, sans-serif" font-size="14">THINK, COMMUNICATE &amp; PRESERVE</text>
  <text x="54" y="606" fill="#B33C49" font-family="ui-monospace, SFMono-Regular, Menlo, monospace" font-size="13">WADA COMBINATION #284</text>
</svg>`;

await sharp(Buffer.from(svg)).png({ compressionLevel: 9 }).toFile("public/og.png");
console.log(`Generated public/og.png at ${width}x${height}.`);
