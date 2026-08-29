# AdSense configuration and consent

AdSense is intentionally disabled in the repository. The committed `_data/runtime.json` contains an empty client ID, ad components render labelled reserved space, and `ads.txt` contains no publisher record.

## Configure a build

The publisher ID is public after activation, but it is still supplied through the build environment to prevent accidental or fake IDs in source.

```bash
ADSENSE_CLIENT_ID=ca-pub-YOUR_REAL_ID npm run configure:adsense
bundle exec jekyll build
```

For GitHub Actions, store `ADSENSE_CLIENT_ID` as a repository variable or secret and run `npm run configure:adsense` before the Jekyll build. The current native GitHub Pages workflow does not run this script; changing the production workflow requires a separate reviewed change.

Ad unit slot IDs must also be created in the AdSense account. Pass a real slot to the reusable include only after approval:

```liquid
{% include ad-slot.html location="article-end" slot="REAL_AD_SLOT_ID" %}
```

Do not put ads beside navigation, download buttons or controls, and do not style content to resemble ads. Keep density reasonable and review mobile layouts for accidental clicks.

## Consent requirements

Before serving personalized or non-personalized Google ads to visitors in the EEA, UK or Switzerland, configure a Google-certified consent-management platform that supports the IAB Transparency and Consent Framework where required. Consent must be collected before relevant non-essential advertising storage or processing begins, and visitors must be able to revisit their choice.

Confirm the latest Google publisher and consent requirements before activation. This document is implementation guidance, not legal advice.

## Final activation steps

1. Receive an approved AdSense publisher ID and create ad units.
2. Configure the environment variable in the reviewed build workflow.
3. Replace the placeholder in `ads.txt` with Google’s exact authorized-seller record.
4. Configure and test consent behavior.
5. Verify ads are labelled, responsive and do not cause layout shift.
6. Test policy, privacy and cookie links from every public page.
