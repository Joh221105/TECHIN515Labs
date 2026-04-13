/** Ensures `./data` and `./data/uploads` exist as soon as the Node server starts. */
export async function register() {
  if (process.env.NEXT_RUNTIME === "nodejs") {
    const { ensureDataDirectories } = await import("./lib/db");
    ensureDataDirectories();
  }
}
