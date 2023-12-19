from django.db.models import Sum
from django.http import HttpResponse

from recipes.models import RecipeIngredient, ShoppingCart
from reportlab.lib.pagesizes import A4
from reportlab.pdfbase import pdfmetrics, ttfonts
from reportlab.pdfgen.canvas import Canvas
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView


class DownloadViewSet(APIView):
    """Viewset for downloading a shopping list."""

    permission_classes = (IsAuthenticated,)

    def canvas_method(self, list, title, filename):
        start_x, start_y = 40, 730
        response = HttpResponse(
            status=status.HTTP_200_OK,
            content_type="application/pdf",
        )
        response["Content-Disposition"] = (
            f"attachment; filename=" f'"{filename}"'
        )
        canvas = Canvas(response, pagesize=A4)
        pdfmetrics.registerFont(
            ttfonts.TTFont("FreeSans", "data/fonts/FreeSans.ttf")
        )
        canvas.setTitle(filename)
        canvas.setFont("FreeSans", 34)
        canvas.drawString(start_x - 10, start_y + 40, title)
        canvas.setFont("FreeSans", 18)
        for number, item in enumerate(list, start=1):
            if start_y < 100:
                start_y = 730
                canvas.showPage()
                canvas.setFont("FreeSans", 18)
            canvas.drawString(start_x, start_y, f"{number}. {item}")
            start_y -= 30
        canvas.showPage()
        canvas.save()
        return response

    def merge_shopping_cart(self):
        """Creates a dictionary list with grocery purchases."""
        shopping_cart = ShoppingCart.objects.filter(
            user=self.request.user
        ).values("recipe")
        items = (
            RecipeIngredient.objects.filter(recipe__in=shopping_cart)
            .values("ingredient__name", "ingredient__measurement_unit")
            .annotate(total_amount=Sum("amount"))
            .order_by("ingredient__name")
        )
        return items

    def get(self, request):
        """Returns a text file from a shopping list."""
        items = self.merge_shopping_cart()
        title = "Список покупок:"
        filename = "Список покупок"
        text_content = []
        for ingr in items:
            name = ingr.get("ingredient__name")
            m_unit = ingr.get("ingredient__measurement_unit")
            amount = ingr.get("ingredient_amount")
            text_content.append(f"{name.capitalize()}: {amount} {m_unit}")
        return self.canvas_method(text_content, title, filename)
