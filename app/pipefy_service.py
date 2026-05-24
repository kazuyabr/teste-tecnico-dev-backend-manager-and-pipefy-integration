class PipefyService:
    CREATE_CARD_MUTATION = """
    mutation {
      createCard(input: {
        pipe_id: "PIPE_ID_HERE"
        fields_attributes: [
          { field_id: "field_nome_id", value: "%(cliente_nome)s" }
          { field_id: "field_email_id", value: "%(cliente_email)s" }
          { field_id: "field_solicitacao_id", value: "%(tipo_solicitacao)s" }
          { field_id: "field_patrimonio_id", value: "%(valor_patrimonio)s" }
        ]
      }) {
        clientMutationId
        card {
          id
          title
        }
      }
    }
    """

    UPDATE_CARD_FIELD_MUTATION = """
    mutation {
      updateCardField(input: {
        id: "%(card_id)s"
        field_id: "field_status_id"
        value: "Processado"
      }) {
        clientMutationId
        success
      }
    }
    """

    UPDATE_PRIORITY_FIELD_MUTATION = """
    mutation {
      updateCardField(input: {
        id: "%(card_id)s"
        field_id: "field_prioridade_id"
        value: "%(prioridade)s"
      }) {
        clientMutationId
        success
      }
    }
    """

    @staticmethod
    def get_create_card_payload(client_data: dict) -> str:
        return PipefyService.CREATE_CARD_MUTATION % {
            "cliente_nome": client_data["cliente_nome"],
            "cliente_email": client_data["cliente_email"],
            "tipo_solicitacao": client_data["tipo_solicitacao"],
            "valor_patrimonio": str(client_data["valor_patrimonio"])
        }

    @staticmethod
    def get_update_status_payload(card_id: str) -> str:
        return PipefyService.UPDATE_CARD_FIELD_MUTATION % {
            "card_id": card_id
        }

    @staticmethod
    def get_update_priority_payload(card_id: str, priority: str) -> str:
        return PipefyService.UPDATE_PRIORITY_FIELD_MUTATION % {
            "card_id": card_id,
            "prioridade": priority
        }