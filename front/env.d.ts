/// <reference types="vite/client" />

declare module '*.vue' {
	import type { DefineComponent } from 'vue'
	// NOTE: This allows TypeScript to understand .vue single-file components.
	const component: DefineComponent<{}, {}, any>
	export default component
}
