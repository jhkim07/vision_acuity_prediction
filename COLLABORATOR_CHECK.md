# GitHub 협력자(Collaborator) 설정 확인 가이드

## 현재 로컬 설정 상태

### Git 사용자 정보
- **Name**: Jin H Kim
- **Email**: jin.kim@gnu.ac.kr
- **Remote URL**: `git@github.com:jhkim07/vision_acuity_prediction.git`

### SSH 키 확인
다음 SSH 공개 키 파일들이 발견되었습니다:
- `~/.ssh/id_ed25519_jh.pub` (jhkim07용으로 추정)
- `~/.ssh/id_ed25519_jin.pub` (jinkimh용으로 추정)
- `~/.ssh/id_rsa.pub`

## GitHub 리포지토리 협력자 확인 방법

### 방법 1: GitHub 웹 인터페이스에서 확인 (권장)

1. **리포지토리 접속**
   - https://github.com/jhkim07/vision_acuity_prediction 로 이동

2. **Settings 탭 클릭**
   - 리포지토리 페이지 오른쪽 상단의 "Settings" 클릭

3. **Collaborators 확인**
   - 왼쪽 사이드바에서 "Collaborators" 또는 "Access" → "Collaborators" 클릭
   - 현재 협력자 목록 확인:
     - `jhkim07` (소유자)
     - `jinkimh` (협력자로 추가되어 있는지 확인)

### 방법 2: GitHub API로 확인 (인증 필요)

```bash
# Personal Access Token이 필요한 경우
curl -H "Authorization: token YOUR_TOKEN" \
  https://api.github.com/repos/jhkim07/vision_acuity_prediction/collaborators
```

### 방법 3: Git 명령어로 테스트

```bash
# jhkim07 계정으로 테스트
git remote set-url origin git@github.com:jhkim07/vision_acuity_prediction.git
git push -u origin main

# jinkimh 계정으로 테스트 (SSH 키 전환 필요)
# SSH config에서 계정별 키 설정이 필요할 수 있음
```

## jinkimh를 협력자로 추가하는 방법

만약 `jinkimh`가 협력자로 추가되어 있지 않다면:

1. **GitHub에 로그인** (`jhkim07` 계정으로)
2. **리포지토리 Settings** → **Collaborators** 이동
3. **"Add people"** 버튼 클릭
4. **`jinkimh`** 사용자명 입력
5. **권한 선택**: 
   - **Write**: push/pull 가능 (일반적으로 이것으로 충분)
   - **Admin**: 모든 권한 (필요시)
6. **초대 발송**
7. **`jinkimh` 계정으로 로그인하여 초대 수락**

## SSH 키 설정 (두 계정 모두 사용하는 경우)

### SSH Config 설정 예시

`~/.ssh/config` 파일에 다음을 추가:

```ssh-config
# jhkim07 계정용
Host github.com-jhkim07
    HostName github.com
    User git
    IdentityFile ~/.ssh/id_ed25519_jh

# jinkimh 계정용
Host github.com-jinkimh
    HostName github.com
    User git
    IdentityFile ~/.ssh/id_ed25519_jin
```

그리고 Git remote URL을 변경:
```bash
# jhkim07 사용 시
git remote set-url origin git@github.com-jhkim07:jhkim07/vision_acuity_prediction.git

# jinkimh 사용 시
git remote set-url origin git@github.com-jinkimh:jhkim07/vision_acuity_prediction.git
```

## 현재 상태 요약

✅ **확인 완료**:
- Git 리포지토리 초기화됨
- 원격 리포지토리 연결됨
- SSH 키 파일 존재 확인

⏳ **확인 필요**:
- GitHub 리포지토리의 협력자 목록 (웹에서 확인 필요)
- `jinkimh` 계정이 협력자로 추가되어 있는지
- 각 계정의 SSH 키가 GitHub에 등록되어 있는지

## 빠른 확인 명령어

```bash
# 현재 Git 사용자 확인
git config user.name
git config user.email

# 원격 리포지토리 확인
git remote -v

# SSH 연결 테스트
ssh -T git@github.com
```

## 문제 해결

### "Permission denied" 오류 발생 시
1. GitHub에 SSH 키가 등록되어 있는지 확인
2. 협력자로 추가되어 있는지 확인
3. SSH 키가 올바른 계정에 연결되어 있는지 확인

### 두 계정을 모두 사용해야 하는 경우
- SSH config 파일을 설정하여 계정별로 다른 키 사용
- 또는 HTTPS + Personal Access Token 사용

