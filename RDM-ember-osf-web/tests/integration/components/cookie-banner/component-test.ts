import { render } from '@ember/test-helpers';
import { hbs } from 'ember-cli-htmlbars';
import { setupRenderingTest } from 'ember-qunit';
import { module, test } from 'qunit';

module('Integration | Component | cookie-banner', hooks => {
    setupRenderingTest(hooks);

    test('it renders', async function(assert) {
        await render(hbs`{{cookie-banner}}`);

        assert.dom(this.element)
            .hasText('The National Institute of Informatics (NII) uses cookies to operate the NII Research Data Cloud service and to improve your user experience. '
                + 'If you intend to use the GakuNin RDM, please read our Privacy Policy and information on NII use of cookies. '
                + 'By clicking Accept or continuing to use our website, you consent to the cookies use on this site. '
                + 'If you do not agree with the cookies use, please change your browser settings to disable cookies or stop using our website. '
                + 'Please be aware that you may not be able to use some functions on our website when you have cookies disabled. Accept');
    });
});
