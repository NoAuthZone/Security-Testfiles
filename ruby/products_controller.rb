require "json"

class ProductsController < ApplicationController
  EXPORT_NAME = /\A[a-zA-Z0-9_-]{1,64}\z/

  def index
    @products = Product.where(status: params[:status])
    render json: @products
  end

  def export
    name = params[:name].to_s
    return head :bad_request unless EXPORT_NAME.match?(name)

    system("zip", "-r", "/exports/#{name}.zip", "/data/products")
    head :ok
  end

  def import
    data = JSON.parse(request.body.read)
    return head :bad_request unless data.is_a?(Array)

    render json: { imported: data.size }
  end

  def done
    redirect_to products_path
  end
end
