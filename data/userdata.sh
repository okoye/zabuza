#!/bin/bash
cat > /tmp/foo.repo <<EOF

[wsgc-snapshotrepo]
name=wsgc-snapshotrepo repository
baseurl=https://snapshotrepo.wsgc.com/artifactory/snapshotrepo
enabled=1
sslverify=false
gpgcheck=0

[wsgc-ext-release-local]
name=wsgc-ext-release-local repository
baseurl=https://artifactory.wsgc.com/artifactory/ext-release-local
enabled=1
sslverify=false
gpgcheck=0
EOF
