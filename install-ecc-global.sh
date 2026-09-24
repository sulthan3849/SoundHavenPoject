#!/bin/bash

# ECC Global Installation Script
echo "Mulai instalasi ECC (Everything Claude Code) secara global..."

# 1. Clone Repositori
echo "Mengambil data dari repositori ECC..."
rm -rf ~/.claude/ecc-temp-install
git clone https://github.com/affaan-m/ECC.git ~/.claude/ecc-temp-install

# 2. Setup Direktori Global
echo "Menyiapkan konfigurasi global di ~/.claude..."
mkdir -p ~/.claude/rules/ecc
mkdir -p ~/.claude/agents
mkdir -p ~/.claude/skills

# 3. Copy Rules & Standar (Terapkan secara global)
echo "Menerapkan rules, agent harness, memory, security, dan research-first development..."
cp -R ~/.claude/ecc-temp-install/rules/common ~/.claude/rules/ecc/
cp -R ~/.claude/ecc-temp-install/rules/typescript ~/.claude/rules/ecc/ 2>/dev/null || true
cp -R ~/.claude/ecc-temp-install/rules/javascript ~/.claude/rules/ecc/ 2>/dev/null || true
cp -R ~/.claude/ecc-temp-install/rules/python ~/.claude/rules/ecc/ 2>/dev/null || true
cp -R ~/.claude/ecc-temp-install/rules/golang ~/.claude/rules/ecc/ 2>/dev/null || true

# 4. Copy Agents dan Skills
echo "Menerapkan subagents dan skills ECC..."
cp -R ~/.claude/ecc-temp-install/agents/* ~/.claude/agents/ 2>/dev/null || true
cp -R ~/.claude/ecc-temp-install/skills/* ~/.claude/skills/ 2>/dev/null || true

# 5. Membersihkan File Sementara
rm -rf ~/.claude/ecc-temp-install

echo "✅ INSTALASI ECC SELESAI!"
echo "ECC sekarang telah diimplementasikan sebagai standar global untuk Claude Code di komputer ini."
echo "Semua project (sekarang dan ke depannya) otomatis menggunakan agent harness, skills, dan memory system ECC."