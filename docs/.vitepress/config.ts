import { withMermaid } from "vitepress-plugin-mermaid";

export default withMermaid({
    title: 'CRTDL',
    description: 'Clinical Resource Transfer Definition Language Documentation',
    ignoreDeadLinks: true,
    base: process.env.VITE_BASE_PATH || '/clinical-resource-transfer-definition-language/',
    appearance: true,
    lastUpdated: true,
    themeConfig: {
        siteTitle: false,
        outline: false,
        aside: false,
        editLink: {
            pattern: 'https://github.com/medizininformatik-initiative/clinical-resource-transfer-definition-language/edit/main/docs/:path',
            text: 'Edit this page on GitHub'
        },

        socialLinks: [
            { icon: 'github', link: 'https://github.com/medizininformatik-initiative/clinical-resource-transfer-definition-language' }
        ],

        footer: {
            message: 'Released under the <a href="https://www.apache.org/licenses/LICENSE-2.0">Apache License 2.0</a>',
        },

        search: {
            provider: 'local'
        },

        nav: [
            { text: 'Home', link: '/' }
        ],

        sidebar: [
            {
                text: 'Home',
                link: '/index.md',
                activeMatch: '^/$'
            },
            {
                text: 'CRTDL Documentation',
                link: '/documentation.md'
            },
            {
                text: 'Changelog',
                link: '/changelog.md'
            }
        ]
    }
})
