package alzwded.openaudiobookify.engine

import android.os.Bundle
import android.speech.tts.TextToSpeech
import java.io.File

class AndroidTtsEngine(
    private val tts: TextToSpeech
) {
    fun synthesize(
        text: String,
        outputFile: File,
        utteranceId: String,
        onSuccess: (File) -> Unit = {},
        onError: (String) -> Unit = {}
    ) {
        val params = Bundle().apply {
            putString(TextToSpeech.Engine.KEY_PARAM_UTTERANCE_ID, utteranceId)
        }
        val result = tts.synthesizeToFile(text, params, outputFile, utteranceId)
        if (result == TextToSpeech.SUCCESS) {
            onSuccess(outputFile)
        } else {
            onError("TTS synthesis failed with code $result")
        }
    }

    fun stop() {
        tts.stop()
    }

    fun shutdown() {
        tts.shutdown()
    }
}
