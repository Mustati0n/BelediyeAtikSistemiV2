# Git Remote Setup

Bu proje yerel Git deposu olarak baslatildi. Uzak repoya baglamak icin GitHub, GitLab veya benzeri bir serviste bos bir repo olusturmak gerekir.

## GitHub Ornegi

1. GitHub'a gir.
2. Yeni repository olustur.
3. Repository adini ornegin `BelediyeAtikSistemiV2` yap.
4. README, `.gitignore` veya license ekleme; repo bos kalsin.
5. GitHub'in verdigi HTTPS veya SSH remote URL'sini kopyala.

## Commit Kimligi

Commit atmak icin Git kullanici adi ve e-posta ister. Bu ayar sadece bu repo icin yapilabilir:

```bash
git config user.name "ADIN veya GitHub kullanici adin"
git config user.email "E-POSTA"
```

GitHub'da e-postani gizli tutmak istersen GitHub'in verdigi `noreply` adresini kullanabilirsin:

```bash
git config user.email "KULLANICI_ADI@users.noreply.github.com"
```

HTTPS ornegi:

```bash
git remote add origin https://github.com/KULLANICI_ADI/BelediyeAtikSistemi.git
git push -u origin main
```

SSH ornegi:

```bash
git remote add origin git@github.com:KULLANICI_ADI/BelediyeAtikSistemi.git
git push -u origin main
```

## Codex Ne Yapabilir?

- Yerel `git init`, `git add`, `git commit` islemlerini yapabilir.
- Commit mesajlarini yazabilir.
- Remote URL'yi sen verdikten sonra `git remote add origin ...` komutunu hazirlayabilir.
- Push icin sistemde GitHub/GitLab yetkisi varsa `git push` calistirabilir.

## Senin Yapman Gereken

- GitHub/GitLab uzerinde bos bir repo olustur.
- Remote URL'yi Codex'e ver.
- HTTPS kullaniyorsan push sirasinda token/giris gerekebilir.
- SSH kullaniyorsan makinede SSH key'in GitHub/GitLab hesabina ekli olmali.
