<script setup>
import { computed } from 'vue'
import DOMPurify from 'dompurify'
import MarkdownIt from 'markdown-it'

const props = defineProps({
  content: {
    type: String,
    default: '',
  },
})

const markdown = new MarkdownIt({
  html: false,
  breaks: true,
  linkify: true,
})

const renderedContent = computed(() =>
  DOMPurify.sanitize(markdown.render(props.content))
)
</script>

<template>
  <div class="markdown-content" v-html="renderedContent"></div>
</template>

<style scoped>
.markdown-content {
  min-width: 0;
  overflow-wrap: anywhere;
}

.markdown-content :deep(> :first-child) {
  margin-top: 0;
}

.markdown-content :deep(> :last-child) {
  margin-bottom: 0;
}

.markdown-content :deep(h1),
.markdown-content :deep(h2),
.markdown-content :deep(h3),
.markdown-content :deep(h4) {
  margin: 1.2em 0 0.55em;
  color: var(--paper);
  font-family: var(--font-body);
  line-height: 1.35;
}

.markdown-content :deep(h1) {
  font-size: 1.35em;
}

.markdown-content :deep(h2) {
  font-size: 1.2em;
}

.markdown-content :deep(h3) {
  font-size: 1.08em;
}

.markdown-content :deep(h4) {
  font-size: 1em;
}

.markdown-content :deep(p),
.markdown-content :deep(ul),
.markdown-content :deep(ol),
.markdown-content :deep(blockquote),
.markdown-content :deep(pre),
.markdown-content :deep(table) {
  margin: 0.65em 0;
}

.markdown-content :deep(ul),
.markdown-content :deep(ol) {
  padding-left: 1.5em;
}

.markdown-content :deep(li + li) {
  margin-top: 0.3em;
}

.markdown-content :deep(a) {
  color: var(--amber);
  text-decoration: none;
}

.markdown-content :deep(a:hover) {
  text-decoration: underline;
}

.markdown-content :deep(blockquote) {
  padding-left: 0.9em;
  color: var(--paper-dim);
  border-left: 2px solid var(--border-strong);
}

.markdown-content :deep(code) {
  padding: 0.1em 0.35em;
  border-radius: 4px;
  background: rgba(0, 0, 0, 0.2);
  font-family: var(--font-mono);
  font-size: 0.9em;
}

.markdown-content :deep(pre) {
  overflow-x: auto;
  padding: 0.9em;
  border: 1px solid var(--border);
  border-radius: var(--radius-md);
  background: rgba(0, 0, 0, 0.2);
}

.markdown-content :deep(pre code) {
  padding: 0;
  background: transparent;
}

.markdown-content :deep(table) {
  width: 100%;
  border-collapse: collapse;
}

.markdown-content :deep(th),
.markdown-content :deep(td) {
  padding: 0.5em 0.65em;
  border: 1px solid var(--border);
  text-align: left;
  vertical-align: top;
}

.markdown-content :deep(th) {
  color: var(--paper);
  background: rgba(255, 255, 255, 0.035);
}

.markdown-content :deep(hr) {
  margin: 1em 0;
  border: 0;
  border-top: 1px solid var(--border);
}
</style>

