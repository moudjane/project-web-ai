<script setup lang="ts">
import AppSidebar from '@/components/layout/AppSidebar.vue'
import ChatWindow from '@/components/chat/ChatWindow.vue'
</script>

<template>
	<div class="flex h-dvh w-full bg-slate-50 text-slate-900 overflow-hidden font-sans">
		<AppSidebar class="hidden md:flex w-72 flex-shrink-0 bg-white border-r border-slate-200" />

		<main class="flex-1 flex flex-col min-w-0">
			<header class="md:hidden flex items-center justify-between p-4 border-b border-slate-200 bg-white/90 backdrop-blur-sm">
				<span class="font-semibold">CogniStack</span>
				<button class="text-slate-500" aria-label="Menu">
					<svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor" class="size-6">
						<path stroke-linecap="round" stroke-linejoin="round" d="M3.75 6.75h16.5M3.75 12h16.5m-16.5 5.25h16.5" />
					</svg>
				</button>
			</header>

			<ChatWindow />
		</main>
	</div>
</template>