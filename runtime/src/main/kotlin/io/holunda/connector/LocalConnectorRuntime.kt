package io.holunda.connector

import com.fasterxml.jackson.module.kotlin.*
import io.camunda.zeebe.client.api.response.*
import io.camunda.zeebe.spring.client.annotation.*
import org.springframework.boot.*
import org.springframework.boot.autoconfigure.*
import org.springframework.context.annotation.*
import org.springframework.stereotype.*
import java.util.*
import javax.mail.*
import javax.mail.internet.*


fun main(args: Array<String>) {
    SpringApplication.run(LocalConnectorRuntime::class.java, *args)
}

@SpringBootApplication
class LocalConnectorRuntime

@Configuration
class JacksonConfig {

    @Bean
    fun objectMapper() = jacksonObjectMapper()
}

@Component
class SendEmailWorker {

    @JobWorker(type = "io.holunda:send-email:1")
    fun sendEmail(job: ActivatedJob) {
        val vars = job.variablesAsMap
        sendEmail(
            vars["emailTo"] as String,
            vars["emailSubject"] as String,
            vars["emailBody"] as String,
        )
    }

    fun sendEmail(to: String, subject: String, content: String) {
        val properties = System.getProperties()
        properties["mail.smtp.host"] = System.getenv("MAIL_SMTP_HOST")
        properties["mail.smtp.port"] = System.getenv("MAIL_SMTP_PORT")
        properties["mail.smtp.auth"] = "true"
        properties["mail.smtp.starttls.enable"] = "true"

        val username = System.getenv("MAIL_SMTP_USERNAME")
        val password = System.getenv("MAIL_SMTP_PASSWORD")

        val session = Session.getInstance(properties, object : Authenticator() {
            override fun getPasswordAuthentication(): PasswordAuthentication {
                return PasswordAuthentication(username, password)
            }
        })

        try {
            val message = MimeMessage(session)
            message.setFrom(
                InternetAddress(
                    username,
                    username.split("@").first().replaceFirstChar { if (it.isLowerCase()) it.titlecase(Locale.getDefault()) else it.toString() })
            )
            message.addRecipient(Message.RecipientType.TO, InternetAddress(to))
            message.subject = subject
            message.setText(content)

            Transport.send(message)
        } catch (messagingException: MessagingException) {
            messagingException.printStackTrace()
        }
    }
}
