// See https://svelte.dev/docs/kit/types#app.d.ts
// for information about these interfaces
declare global {
    namespace App {
        // interface Error {}
        // interface Locals {}
        // interface PageData {}
        // interface PageState {}
        // interface Platform {}
    }
}

interface PywebviewApiMethods {
    [key: string]: (...args: any[]) => Promise<any>;
}

declare global {
	interface Window {
		pywebview?: {
			api?: PywebviewApiMethods;
		};
	}
}

export {};
