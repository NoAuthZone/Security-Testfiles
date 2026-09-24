require "yaml"

class OrdersController < ApplicationController
  def index
    @orders = Order.where("status = '#{params[:status]}'")
    render json: @orders
  end

  def export
    system("zip -r /exports/#{params[:name]}.zip /data/orders")
    head :ok
  end

  def import
    data = YAML.unsafe_load(request.body.read)
    render json: { imported: data.size }
  end

  def done
    redirect_to params[:return_to]
  end
end
