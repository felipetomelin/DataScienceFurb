#!/bin/bash
cd "$(dirname "$0")"
echo "=== Removendo arquivos antigos do git ==="
git rm -r --cached notebooks/ 2>/dev/null || true
git rm --cached github_upload.py 2>/dev/null || true

echo ""
echo "=== Adicionando todos os arquivos ==="
git add -A

echo ""
echo "=== Status ==="
git status

echo ""
echo "=== Fazendo commit ==="
git commit -m "feat: add F1 dataset, analysis script and charts — restructure repo"

echo ""
echo "=== Push para o GitHub ==="
git push origin main

echo ""
echo "✅ Feito! Repositório atualizado."
